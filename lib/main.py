#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# main.py
#
# Copyright (c) 2014, Paul Holleis, Marko Luther
# All rights reserved.
# 
# 
# LICENSE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import platform
import json
import numpy
import time
import numpy as np
from functools import reduce as freduce
import numpy.polynomial.polynomial as poly

import sip
try:
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)
except:
    pass

# PyQt5:
#    from PyQt5.QtWidgets import (QApplication,QMainWindow,QWidget,QDialog,QMessageBox,QMenuBar,QTextBrowser,QAction,QLineEdit,QVBoxLayout,QFileDialog)
#    from PyQt5.QtGui import (QIcon)
#    from PyQt5.QtCore import (QCoreApplication,QTimer,QSettings,QLocale,QTranslator,QDir,QFileInfo,QEvent)

# PyQt4:
from PyQt4.QtGui import (QApplication,QMainWindow,QDialog,QMessageBox,QAction,QFileDialog,QIcon,QItemSelection,QItemSelectionModel,QProgressDialog,QDialogButtonBox)
from PyQt4.QtCore import (QProcess,QTimer,QSettings,QLocale,QTranslator,QDir,QFileInfo,QEvent,Qt,pyqtSignal)


from lib import __version__
import lib.serialport
import lib.scales
from uic import MainWindowUI, AboutDialogUI, PreferencesDialogUI, CalibDialogUI
import uic.resources as resources


try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

if sys.version < '3':
    def u(x): # convert to unicode string
        return unicode(x)
else:
    def u(x): # convert to unicode string
        return str(x)
        

###########################################################################################################################################
#
# Tonino Application
#
 
class Tonino(QApplication):
    def __init__(self, args):
        super(Tonino, self).__init__(args)
        self.aw = None
        
        # constants
        if platform.system() == 'Windows':
            self.avrdude = "avrdude.exe"
        else:
            self.avrdude = "avrdude"
        self.avrdude_conf = "avrdude.conf"
        self.included_firmware_name = None
        self.included_firmware_version = None # a list of three int indicating major, minor and build versions of the included firmware
        
        # calib constants
        self.std_calib_low_r = 2320. # brown disk red reading
        self.std_calib_low_b = 1470. # brown disk blue reading
        self.std_calib_high_r = 11300. # red disk red reading
        self.std_calib_high_b = 3050. # red disk blue reading
        self.std_calib_target_low = 1.5
        self.std_calib_target_high = 3.7
        # the tolerance distance of the calib measurements to the expected values above that still allow the recognition
        self.calib_red_range_low = 1200
        self.calib_red_range_high = 4200
        self.calib_blue_range_low = 750
        self.calib_blue_range_high = 1450
        
        # variables
        self.workingDirectory = None
        self.currentFile = None
        self.currentFileDirty = False # should be cleared on save and set on any modification
        self.maxRecentFiles = 10
        self.recentFiles = []
        self.paramSeparatorChar = " " # separator char used by the Tonino serial protocol
        self.toninoPort = None # port of the connected Tonino
        self.toninoFirmwareVersion = None # a list of three int indicating major, minor and build versions of the connected device
        self.toninoControllerType = None # the type of the Tonino micro controller (Arduino Nano, Micro,..)
        self.scales = lib.scales.Scales(self)
        self.ser = lib.serialport.SerialPort() # the serial connection object
        # calibration raw readings
        self.calib_low_r = None
        self.calib_low_b = None
        self.calib_high_r = None
        self.calib_high_b = None
        self.retrieveIncludedFirmware()
      
    def clearCalibReadings(self):
        self.calib_low_r = None
        self.calib_low_b = None
        self.calib_high_r = None
        self.calib_high_b = None
        
    # detects if the given red and blue readings are in the range of either the low or the high calibration disk
    # and sets the corresponding variables accordingly
    def setCalibReadings(self,r,b):
        if abs(r - self.std_calib_low_r) < self.calib_red_range_low and abs(b - self.std_calib_low_b) < self.calib_blue_range_low:
            # calib_low disk recognized
            self.calib_low_r = r
            self.calib_low_b = b
        elif abs(r - self.std_calib_high_r) < self.calib_red_range_high and abs(b - self.std_calib_high_b) < self.calib_blue_range_high:
            # calib_high disk recognized
            self.calib_high_r = r
            self.calib_high_b = b
            
    def getCalibLow(self):
        if self.calib_low_r and self.calib_low_b:
            return (self.calib_low_r,self.calib_low_b)
            
    def getCalibHigh(self):
        if self.calib_high_r and self.calib_high_b:
            return (self.calib_high_r,self.calib_high_b)
            
    def updateCalib(self):
        if self.toninoPort:
            calib_low = self.getCalibLow()
            calib_high = self.getCalibHigh()            
            if calib_low and calib_high:
                # both calibs have been set, generate and upload the new calibration data to the connected Tonino
                target_low_rb = self.std_calib_target_low
                target_high_rb = self.std_calib_target_high
                calib_low_rb = calib_low[0]/calib_low[1]
                calib_high_rb = calib_high[0]/calib_high[1]
                c = poly.polyfit([calib_low_rb,calib_high_rb],[target_low_rb,target_high_rb],1)
                # transfer result to connected Tonino
                self.setCal(self.toninoPort,[c[1],c[0]])
                self.aw.showMessage(_translate("Message","Calibration updated",None))
        
    def getWorkingDirectory(self):
        if not self.workingDirectory:    
            if platform.system() in ['Darwin','Linux']:
                self.workingDirectory = QDir().homePath() + "/Documents/"
            else:
                self.workingDirectory = QDir().homePath()
        return self.workingDirectory
                    
    def setWorkingDirectory(self,f):
        if f:
            filepath_dir = QDir()
            filepath_dir.setPath(f)
            filepath_elements = filepath_dir.absolutePath().split("/")[:-1] # directories as QStrings (without the filename)
            self.workingDirectory = freduce(lambda x,y: x + '/' + y, filepath_elements) + "/"

    def retrieveIncludedFirmware(self):
        qd = QDir()
        qd.setCurrent(resources.getResourcePath())
        fileinfos = qd.entryInfoList(["tonino-*.hex"],QDir.Files | QDir.Readable,QDir.SortFlags(QDir.Name | QDir.Reversed))
        if len(fileinfos) > 0:
            fn = fileinfos[0].fileName()
            try:
                self.included_firmware_version = [int(s) for s in fn.split("-")[1].rsplit(".")[:3]]
                self.included_firmware_name = fn
            except:
                pass
        
    # returns True if version v1 is greater than v2 and False otherwise and if the arguments are malformed
    def versionGT(self,v1,v2):
        if v1 != None and v2 != None and len(v1) == len(v2) == 3:
            for i in range(3):
                if v1[i] > v2[i]:
                    return True
                elif v1[i] < v2[i]:
                    return False
            return False
        return False
                
    
    # load Tonino configuration on double click a *.toni file in the Finder while Tonino.app is already running
    def event(self, event):
        if event.type() == QEvent.FileOpen:
            try:
                self.aw.loadFile(event.file())
            except Exception:
                pass
            return 1
        return super(Tonino, self).event(event) 

    def strippedName(self, fullfilename):
        return QFileInfo(fullfilename).fileName()
        
    def strippedDir(self, fullfilename):
        return QFileInfo(fullfilename).dir().dirName()


#
# Application Settings
#
                
    # loads the application settings at application start. See the oppposite saveSettings()
    def loadSettings(self):
        try: 
            settings = QSettings()
            if settings.contains("resetsettings"):
                self.resetsettings = settings.value("resetsettings",self.resetsettings).toInt()[0]
                if self.resetsettings:
                    self.resetsettings = 0
                    return  #don't load any more settings. They could be corrupted. Stop here.
            # restore geometry
            if self.aw and settings.contains("geometry"):
                self.aw.restoreGeometry(settings.value("geometry"))
            # restore the working directory
            if settings.contains("workingDirectory"):
                self.workingDirectory = settings.value("workingDirectory")
            # restore recent files
            if settings.contains("recentFiles"):
                self.recentFiles = settings.value("recentFiles")
        except:
            if self.aw:
                QMessageBox.information(self.aw,_translate("Message", "Error",None),_translate("Message", "Loading settings failed",None))

    # saves the application settings when closing the application. See the oppposite loadSettings()
    def saveSettings(self):
        try:
            settings = QSettings()
            if self.aw:
                #save window geometry
                settings.setValue("geometry",self.aw.saveGeometry())
            # store the actual working directory
            settings.setValue("workingDirectory",self.getWorkingDirectory())
            # store recent files
            settings.setValue("recentFiles",self.recentFiles)
        except:
            self.resetsettings = 0 # ensure that the corrupt settings are not loaded on next start and thus overwritten
            if self.aw:
                QMessageBox.information(self.aw,_translate("Message", "Error",None),_translate("Message", "Saving settings failed",None))
        
#
# Tonino Serial Protocol
#  
     
    # turns a response in a value list with elements of elemType of length numOfArgs or none
    def response2values(self,response,elemType,numOfArgs):
        res = None
        values = response.split(self.paramSeparatorChar)
        if len(values) == numOfArgs:
            res = [elemType(v) for v in values]
        return res
        
    def formatCommand(self,cmd,values,onSend=False):
        return cmd + (" " if onSend else ":") + self.paramSeparatorChar + self.paramSeparatorChar.join([str(v) for v in values])
    
    def resetArduino(self):
        if self.toninoPort:
            self.ser.sendReset(self.toninoPort)
 
    def uploadFirmware(self):
        resourcePath = resources.getResourcePath()
        resourceBinaryPath = resources.getResourceBinaryPath()
        avrdude = resourceBinaryPath + self.avrdude
        avrdudeconf = resourceBinaryPath + self.avrdude_conf
        toninoSketch = resourcePath + self.included_firmware_name
        args = ["-C",avrdudeconf,"-q","-q","-patmega328p","-carduino","-P",self.toninoPort,"-b57600","-D","-Uflash:w:" + u(toninoSketch) + ":i"]
        process = QProcess(self)
        process.finished.connect(self.uploadFirmwareDone)
        process.start(avrdude,args)
        self.aw.showprogress.emit()
        
    def uploadFirmwareDone(self,exitCode,exitStatus):
        if exitCode:
            # update failed
            self.aw.showMessage(_translate("Message","Firmware update failed",None),msecs=10000)
        else:
            self.aw.showMessage(_translate("Message","Firmware successfully updated",None),msecs=10000)
        self.aw.endprogress.emit()
        
    # requests version string from connected Tonino
    # returns None if communication fails and the version object (a list of three integers: major, minor, build) otherwise
    # cmd: TONINO
    # onStartup should be true if this is the first check after app start    
    def getToninoFirmwareVersion(self,port,onStartup=False):
        res = None
        if port:
            # send "TONINO" to the given serial port and returns the successful parsed version as int list
            # [major,minor,build]
            if onStartup:
                time.sleep(.1) # if device is already connected it should be already starting up
            else:
                time.sleep(.8) # wait a moment until the Arduino allows to open the port and finished its serial device init
            self.ser.openPort(port) # on Mac OS X this will trigger an Arduino reset
            if onStartup:
                time.sleep(2.5)  # wait a second until the Arduino Nano did a reset
            else:
                time.sleep(2)  # wait a second until the Arduino Nano did a reset
            self.ser.sendCommand(port,"",False) # first send a dummy empty cmd to get serial started
            response = self.ser.sendCommand(port,"TONINO")
            if response:
                res = self.response2values(response,int,3)
        return res
        
    
    # cmd: GETBRIGHTNESS (0-15)
    def getDisplayBrightness(self,port):
        res = None
        if port:
            response = self.ser.sendCommand(port,"GETBRIGHTNESS")
            if response:
                res = self.response2values(response,int,1)
        return res
    
    # cmd: SETBRIGHTNESS (0-15)
    def setDisplayBrightness(self,port,brightness):
        if port:
            self.ser.sendCommand(port,self.formatCommand("SETBRIGHTNESS",[brightness]))
        
    # cmd: GETSCALING
    def getScale(self,port):
        res = None
        if port:
            response = self.ser.sendCommand(port,"GETSCALING")
            if response:
                res = self.response2values(response,float,4)
        return res
        
    # cmd: SETSCALING
    def setScale(self,port,scaling):
        if port:
            self.ser.sendCommand(port,self.formatCommand("SETSCALING",scaling))
        
    # cmd: SETCAL
    def setCal(self,port,cal):
        if port:
            self.ser.sendCommand(port,self.formatCommand("SETCAL",cal,onSend=True))
        
    # cmd: I_SCAN
    def getRawCalibratedReading(self,port):
        res = None
        response = self.ser.sendCommand(port,"I_SCAN")
        if response:
            res = self.response2values(response,float,1)
        return res
        
    # cmd: II_SCAN
    def getRawReadings(self,port):
        res = None
        response = self.ser.sendCommand(port,"II_SCAN")
        if response:
            res = self.response2values(response,float,5)
        return res
        
    # cmd: D_SCAN
    def getBlackReadings(self,port):
        res = None
        response = self.ser.sendCommand(port,"D_SCAN")
        if response:
            res = self.response2values(response,float,4)
        return res
        
    # cmd: RESETDEF
    def reset2Defaults(self,port):
        if port:
            self.ser.sendCommand(port,"RESETDEF")

        
#
# Load and Save Tonino Scales
#
    
    # load scale from file
    # returns True if loading suceeded
    def loadScale(self,filename):
        try:
            if self.aw.verifyDirty():  
                import io
                infile = io.open(filename, 'r', encoding='utf-8')
                obj = json.load(infile)
                infile.close()          
                self.scales.setScale(obj)
                self.contentCleared()
                return True
            else:
                return False
        except:
            if self.aw:
                QMessageBox.critical(self.aw,_translate("Message", "Error",None),_translate("Message", "Scale could not be loaded",None))
            return False
        
    # write current scale to file
    # returns True if saving suceeded
    def saveScale(self,filename):
        try:
            cs = self.scales.getScale()
            if cs:
                outfile = open(filename, 'w')
                json.dump(cs, outfile, ensure_ascii=True)
                outfile.write('\n')
                outfile.close()
                self.contentCleared()
                return True
            else:
                return False
        except:
            if self.aw:
                QMessageBox.critical(self.aw,_translate("Message", "Error",None),_translate("Message", "Scale could not be saved",None))
            return False
            
    def applyScale(self,filename):
        try:
            import io
            infile = io.open(filename, 'r', encoding='utf-8')
            obj = json.load(infile)
            infile.close()
            self.scales.applyScale(obj)
            return True
        except:
            if self.aw:
                QMessageBox.critical(self.aw,_translate("Message", "Error",None),_translate("Message", "Scale could not be applied",None))
            return False
    
            
    def contentModified(self):
        self.currentFileDirty = True
        self.aw.updateWindowTitle()
        self.aw.ui.actionSave.setEnabled(True)
        self.aw.ui.actionSave_As.setEnabled(True)
        
    def contentCleared(self):
        self.currentFileDirty = False
        self.currentFile = None
        self.aw.updateWindowTitle()
        if len(self.scales.getCoordinates()) > 0:
            # if there is content, but unmodified we still allow Save and SaveAs
            self.aw.ui.actionSave_As.setEnabled(True)
            self.aw.ui.actionSave.setEnabled(True)
        else:
            self.aw.ui.actionSave_As.setEnabled(False)
            self.aw.ui.actionSave.setEnabled(False)


###########################################################################################################################################
#
# Dialog Controllers
#

class ToninoDialog(QDialog):
    def __init__(self, parent=None):
        super(ToninoDialog,self).__init__(parent)

    def keyPressEvent(self,event):
        key = int(event.key())
        if key == 16777216: #ESCAPE
            self.close()
            
class PreferencesDialog(ToninoDialog):
    def __init__(self, parent = None, app=None):
        super(PreferencesDialog,self).__init__(parent)        
        self.app = app
        self.ui = PreferencesDialogUI.Ui_Preferences()
        self.ui.setupUi(self)
        self.displayBrightness = None
        self.lastBrightness = None # remember the last setting to avoid resending the same setting
        if self.app.toninoPort:
            try:
                v = self.app.getDisplayBrightness(self.app.toninoPort)
                self.displayBrightness = self.lastBrightness = v[0]
                self.ui.displaySlider.setValue(self.displayBrightness)
            except:
                pass
        else:
            self.ui.groupBoxToninoDisplay.setEnabled(False)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        self.ui.displaySlider.setTracking(False) # no valueChanged signals while moving
        self.ui.displaySlider.valueChanged.connect(self.sliderChanged)
        
    def sliderChanged(self):
        v = self.ui.displaySlider.value()
        if self.displayBrightness != None and self.lastBrightness != v:
            self.app.setDisplayBrightness(self.app.toninoPort,v)
            self.lastBrightness = v # remember this as last setting

    def accept(self):
        self.done(0)
        
    def reject(self):
        self.app.setDisplayBrightness(self.app.toninoPort,self.displayBrightness)
        self.done(0)
    
    def close(self):
        self.reject()

class CalibDialog(ToninoDialog):
    def __init__(self, parent = None, app=None):
        super(CalibDialog,self).__init__(parent)
        self.setModal(True)
        self.app = app
        self.ui = CalibDialogUI.Ui_Dialog()
        self.ui.setupUi(self)
        # disable elements
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.calibLowLabel.setEnabled(False)
        self.ui.calibHighLabel.setEnabled(False)
        # connect actions
        self.ui.pushButtonScan.clicked.connect(self.scan)
        # clear previous calibrations
        self.app.clearCalibReadings()

    def scan(self):
        try:
            raw_readings1 = self.app.getRawReadings(self.app.toninoPort)
            time.sleep(.75)
            dark_readings = self.app.getBlackReadings(self.app.toninoPort)
            time.sleep(.75)
            raw_readings2 = self.app.getRawReadings(self.app.toninoPort)
            if raw_readings1 == None:
                raw_readings1 = raw_readings2
            if raw_readings2 == None:
                raw_readings2 = raw_readings1
            if raw_readings1 and raw_readings2 and len(raw_readings1)>3 and len(raw_readings2)>3:
                r = (raw_readings1[1] + raw_readings2[1]) / 2. - dark_readings[1]
                b = (raw_readings1[3] + raw_readings2[3]) / 2. - dark_readings[3]
                self.app.setCalibReadings(r,b)
                calib_low = self.app.getCalibLow()
                calib_high = self.app.getCalibHigh()
                # if low reading is set enable the clib_low
                if calib_low:
                    self.ui.calibLowLabel.setEnabled(True)
                if calib_high:
                    self.ui.calibHighLabel.setEnabled(True)
                # if both, low and high readings are set, enable the OK button  
                if calib_low and calib_high:
                    self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        except:
            pass
        
    def accept(self):
        self.app.updateCalib()
        self.done(0)
        
    def reject(self):
        self.done(0)
    
    def close(self):
        self.reject()


###########################################################################################################################################
#
# Main Application Window UI Controller
#

class ApplicationWindow(QMainWindow):
    showprogress = pyqtSignal()
    endprogress = pyqtSignal()
    
    def __init__(self, parent=None,app=None):
        super(QMainWindow, self).__init__(parent)
        self.app = app
        self.ui = MainWindowUI.Ui_MainWindow()
        self.ui.setupUi(self)
        self.app.aw = self

        # constants
        self.toninoFileExtension = "toni"
        self.toninoFileFilter = "Text files (*.toni)"
        self.windowTitle = _translate("MainWindow","Tonino",None)
        self.fastCheck = 1000
        self.slowCheck = 2000
        self.checkDecay = 5*60 # after 5min turn to slowCheck
        self.currentFileDirtyPrefix = "*"
        self.tableheaders = ["T",_translate("MainWindow","Name",None)]
        self.popupadd = _translate("MainWindow","add",None)
        self.popupdelete = _translate("MainWindow","delete",None)

        # variables
        self.progress = None # holds the QProgressDialog indicating the firmware update progress
        self.deviceCheckCounter = 0
        self.resetsettings = 0 # if set, settings are not loaded on app start
        self.deviceCheckInterval = self.fastCheck # serial device check interval in ms
        self.ports = None # a list of detected serial ports 
        self.recentFileActs = []
        self.recentApplyActs = []
        
        # inital UI configuration
        self.setWindowTitle(self.windowTitle)
        self.disconnectTonino(True)
        
        # create recent files menu actions
        for i in range(self.app.maxRecentFiles):
            self.recentFileActs.append(
                    QAction(self, visible=False,
                            triggered=self.openRecent))
            self.recentApplyActs.append(
                    QAction(self, visible=False,
                            triggered=self.applyRecent))
        
        self.app.loadSettings()
        
        # populate recent files menu
        for i in range(self.app.maxRecentFiles):
            self.ui.menuOpen_Recent.addAction(self.recentFileActs[i])
            self.ui.menuOpen_ApplyRecent.addAction(self.recentApplyActs[i])
        self.updateRecentFileActions()
        
        # connect the buttons,sliders and menu actions
        self.ui.actionAbout.triggered.connect(self.showAbout)
        self.ui.actionAboutQt.triggered.connect(self.showAboutQt)
        self.ui.actionSettings.triggered.connect(self.showPreferences)
        self.ui.actionOpen.triggered.connect(self.openFile)
        self.ui.actionSave.triggered.connect(self.saveFile)
        self.ui.actionSave_As.triggered.connect(self.saveAsFile)
        self.ui.actionApply.triggered.connect(self.applyFile)
        self.ui.pushButtonUpload.clicked.connect(self.uploadScale)
        self.ui.pushButtonDefaults.clicked.connect(self.defaults)
        self.ui.pushButtonAdd.clicked.connect(lambda _: self.addCoordinate(True))
        self.ui.pushButtonDelete.clicked.connect(self.deleteCoordinates)
        self.ui.pushButtonClear.clicked.connect(self.clearCoordinates)
        self.ui.pushButtonSort.clicked.connect(self.sortCoordinates)
        self.ui.pushButtonCalib.clicked.connect(self.showCalib)
        self.ui.degreeSlider.setTracking(False) # no valueChanged signals while moving
        self.ui.degreeSlider.valueChanged.connect(self.sliderChanged)
        self.ui.actionCut.triggered.connect(self.actionCut)
        self.ui.actionCopy.triggered.connect(self.actionCopy)
        self.ui.actionPaste.triggered.connect(self.actionPaste)
        
        # enable buttons
        self.ui.pushButtonDelete.setEnabled(False)
        
        # initalize dirty state        
        self.app.contentCleared()
        
        # move slider
        self.ui.degreeSlider.setValue(self.app.scales.getPolyfitDegree())
        
        # connect coordinates table view to model
        self.ui.tableView.setModel(self.app.scales)
        self.ui.tableView.setColumnWidth(0,50)
        self.ui.tableView.setItemDelegate(lib.scales.ValidatedItemDelegate())
        
        # connect the table selection
        self.ui.tableView.selectionModel().selectionChanged.connect(self.selectionChanged)
                
        self.showprogress.connect(self.showProgress)
        self.endprogress.connect(self.endProgress)
        
        #Fake entries to get translations for the Mac Application Menu
        _mac_services = _translate("MAC_APPLICATION_MENU", "Services", None)
        _mac_hide = _translate("MAC_APPLICATION_MENU", "Hide %1", None)
        _mac_hideothers = _translate("MAC_APPLICATION_MENU", "Hide Others", None)
        _mac_showall = _translate("MAC_APPLICATION_MENU", "Show All", None)
        _mac_preferences = _translate("MAC_APPLICATION_MENU", "Preferences...", None)
        _mac_quit = _translate("MAC_APPLICATION_MENU", "Quit %1", None)
        _mac_about = _translate("MAC_APPLICATION_MENU", "About %1", None)
                
        _dialog_ok = _translate("QDialogButtonBox", "OK", None)
        _dialog_save = _translate("QDialogButtonBox", "Save", None)
        _dialog_dont_save = _translate("QDialogButtonBox", "Don't Save", None)
        _dialog_open = _translate("QDialogButtonBox", "Open", None)
        _dialog_cancel = _translate("QDialogButtonBox", "Cancel", None)
        _dialog_close = _translate("QDialogButtonBox", "Close", None)
        _dialog_abort = _translate("QDialogButtonBox", "Abort", None)

        
    def actionCut(self):
        self.actionCopy()
        self.deleteCoordinates()

    def actionCopy(self):
        clipboard = QApplication.clipboard()
        selected = self.app.scales.getSelectedCoordinates()
        selected_text = self.app.scales.coordinates2text(selected)
        clipboard.setText(selected_text)

    def actionPaste(self):
        coordinates = None
        try:
            clipboard = QApplication.clipboard()
            self.app.scales.addCoordinates(self.app.scales.text2coordinates(clipboard.text()))
        except:
            pass
        
    def showProgress(self):
        self.progress = QProgressDialog(_translate("Message","Updating firmware...",None), None, 0, 20, self)
        self.progress.setCancelButton(None)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setAutoClose(False)
        self.progress.show()
        for i in range(20):
            if self.progress:
                self.progress.setValue(i)
            time.sleep(1)
        if self.progress:
            self.progress.setRange(0,0)
            self.progress.setValue(0)
            self.progress.show()
        
    def endProgress(self):
        self.disconnectTonino()
        if self.progress:
            self.progress.cancel()
            self.progress = None
        self.ports = None # this ensures that the already connected Tonino is rediscovered

#
# Keyboard Handling
#
    
    def keyPressEvent(self,event):
        key = int(event.key())
        if key == 16777219: # backspace
            self.deleteCoordinates()
        
        
    
#
# File Handling
#

    def openRecentFile(self):
        action = self.sender()
        if action:
            self.loadFile(action.data().toString())

    # generic load file dialog interface
    def fileDialog(self,msg,path=None,ffilter=None,openFile=True):
        try:
            if path == None:   
                path = self.app.getWorkingDirectory()
            if openFile:
                res = QFileDialog.getOpenFileName(self,msg,path,ffilter)
            else:
                res = QFileDialog.getSaveFileName(self,msg,path,ffilter)

            if res != None and res != "":
                if isinstance(res,list):
                    res = res[0]
                self.app.setWorkingDirectory(res)
            return res
        except:
            return None

    def updateRecentFileActions(self):
        files = self.app.recentFiles
        if not files:
            files = []
        strippedNames = list(map(self.app.strippedName,files))
        numRecentFiles = min(len(files), self.app.maxRecentFiles)
        for i in range(numRecentFiles):
            strippedName = self.app.strippedName(files[i])
            if strippedNames.count(strippedName) > 1:
                text = "&%s (%s)" % (strippedName, self.app.strippedDir(files[i]))
            else:
                text = "&%s" % strippedName
            self.recentFileActs[i].setText(text)
            self.recentFileActs[i].setData(files[i])
            self.recentFileActs[i].setVisible(True)
            self.recentApplyActs[i].setText(text)
            self.recentApplyActs[i].setData(files[i])
            self.recentApplyActs[i].setVisible(True)
        for j in range(numRecentFiles, self.app.maxRecentFiles):
            self.recentFileActs[j].setVisible(False)
            self.recentApplyActs[j].setVisible(False)
            
    def setCurrentFile(self, filename):
        self.app.currentFile = filename
        if filename:
            # update window title
            self.updateWindowTitle()
            # update recent file menu
            try:
                self.app.recentFiles = list(filter((filename).__ne__, self.app.recentFiles))
            except ValueError:
                pass
            self.app.recentFiles.insert(0, filename)
            del self.app.recentFiles[self.app.maxRecentFiles:]
            self.updateRecentFileActions()
        else:
            self.setWindowTitle(self.windowTitle)
        
    def updateWindowTitle(self):
        if self.app.currentFile:
            # a file is loaded
            filename = self.app.strippedName(self.app.currentFile)
            if self.app.currentFileDirty:
                # the content has changed
                self.setWindowTitle(self.currentFileDirtyPrefix + filename + self.currentFileDirtyPrefix)
            else:
                # all changes are saved
                self.setWindowTitle(filename)
        else:
            self.setWindowTitle(self.windowTitle)
         
    def loadFile(self,filename):
        if filename:
            qfile = QFileInfo(filename)
            file_suffix = qfile.suffix()
            if file_suffix == self.toninoFileExtension:
                res = self.app.loadScale(filename)
                if res:
                    self.setCurrentFile(filename)
    
    def applyScale(self,filename):
        if filename:
            qfile = QFileInfo(filename)
            file_suffix = qfile.suffix()
            if file_suffix == self.toninoFileExtension:
                self.app.applyScale(filename)
           
    def openFile(self):
        self.loadFile(self.fileDialog(_translate("Dialog","Open Scale",None),ffilter=self.toninoFileFilter))
        
    def openRecent(self):
        action = self.sender()
        if action:
            self.loadFile(action.data())
    
    def saveFile(self):
        currentFile = self.app.currentFile
        if currentFile:
            self.app.saveScale(currentFile)
            self.setCurrentFile(currentFile)
        else:
            self.saveAsFile()
        
    def saveAsFile(self):
        filename = self.fileDialog(_translate("Dialog","Save As",None),ffilter=self.toninoFileFilter,openFile=False)
        if filename:
            res = self.app.saveScale(filename)
            if res:
                self.setCurrentFile(filename)
                self.updateWindowTitle()
                
    def applyFile(self):
        self.applyScale(self.fileDialog(_translate("Dialog","Apply Scale",None),ffilter=self.toninoFileFilter))
        
    def applyRecent(self):
        action = self.sender()
        if action:
            self.applyScale(action.data())
            
#
# Buttons
#

    def defaults(self):
        self.app.reset2Defaults(self.app.toninoPort)
        self.app.scales.setDeviceCoefficients(self.app.getScale(self.app.toninoPort))
        self.showMessage(_translate("Message","Tonino reset to defaults",None))
    
    def uploadScale(self):
        scale = self.app.scales.getCoefficients()        
        scale = [0.]*(4-len(scale)) + scale # ensure a 4 element scale
        self.app.setScale(self.app.toninoPort,scale)
        self.app.scales.setDeviceCoefficients(self.app.getScale(self.app.toninoPort))
        self.showMessage(_translate("Message","Scale uploaded",None))
        
    def addCoordinate(self,retry=True):
        try:
            raw_x = self.app.getRawCalibratedReading(self.app.toninoPort)
            if raw_x:
                if np.isnan(raw_x[0]) or raw_x[0] == float('inf'):
                    self.showMessage(_translate("Message","Coordinate out of range",None),msecs=10000)
                else:
                    self.app.scales.addCoordinate(raw_x[0],None)
                    QTimer.singleShot(0, self.ui.tableView.scrollToBottom)
            else:
                if retry:
                    self.addCoordinate(retry=False)
                else:
                    self.showMessage(_translate("Message","Coordinate out of range",None),msecs=10000)
        except:
            pass

    def deleteCoordinates(self):
        self.app.scales.deleteCoordinates([s.row() for s in self.ui.tableView.selectionModel().selectedRows()])
        
    def clearCoordinates(self):
        self.app.scales.clearCoordinates()
        
    def sortCoordinates(self):
        self.app.scales.sortCoordinates()
        
#
# Slider
#

    def sliderChanged(self):
        self.app.scales.setPolyfitDegree(self.ui.degreeSlider.value())

    
#
# Measurements Table
#        
        
    def selectionChanged(self, newSelection, oldSelection):
        if self.ui.tableView.selectionModel().selectedRows():
            self.ui.pushButtonDelete.setEnabled(True)
        else:
            self.ui.pushButtonDelete.setEnabled(False)
        self.ui.widget.canvas.redraw()
            
    def getSelectedRows(self):
        if self.ui.tableView and self.ui.tableView.selectionModel():
            return [s.row() for s in self.ui.tableView.selectionModel().selectedRows()]
        else:
            return []
            
    # invoked by clicks on coordinates in the graph
    def toggleSelection(self,row):
        self.ui.tableView.setFocus()
        self.ui.tableView.selectionModel().select(QItemSelection(self.app.scales.createIndex(row,0),self.app.scales.createIndex(row,1)), 
            QItemSelectionModel.Toggle)     
        
        
#
# Dialogs
#

    def showAboutQt(self):
        QApplication.instance().aboutQt()
        
    def showAbout(self):
        Dialog = QDialog(self)
        ui = AboutDialogUI.Ui_Dialog()
        ui.setupUi(Dialog)
        version = _translate("Dialog", "Version", None) + " " + __version__
        if self.app.included_firmware_version:        
            version += " (" + self.version2str(self.app.included_firmware_version,prefix="") + ")"
        ui.versionLabel.setText(version)
        ui.pushButton.clicked.connect(Dialog.accept)
        Dialog.show()
        
    def showPreferences(self):
        prefs = PreferencesDialog(self,self.app)
        prefs.show()
        
    def showCalib(self):
        self.calibs = CalibDialog(self,self.app)
        self.calibs.show()
        
        
#
# Firmware Update
#                   
            
    def updateFirmware(self):
        if self.app.toninoPort:
            # disconnect established serial connection
            self.app.ser.closePort()
        self.app.resetArduino()
        self.app.uploadFirmware()
        self.disconnectTonino()

    
#
# Tonino Auto Connect
#   
    
    # Tonino version to formatted string
    def version2str(self,v,prefix="v"):
        return prefix + ".".join([str(e) for e in v])

    # checks all ports for connected Toninos
    # returns (port,version) of the first successful connect or None
    # onStartup should be true if this is the first check after app start
    def checkPorts(self,ports,onStartup=False):
        res = None
        if ports and len(ports):
            for p in ports:
                self.showMessage(_translate("Message","Connecting...",None),msecs=3000)
                self.app.processEvents()
                version = self.app.getToninoFirmwareVersion(p,onStartup)
                if version:
                    res = p,version
                    break
        return res


    def showMessage(self,s,msecs=0):
        self.ui.status.showMessage(s,msecs)
        
    def toninoConnected(self):
        return self.app.toninoPort

    def checkFirmwareVersion(self):
        if self.app.versionGT(self.app.included_firmware_version,self.app.toninoFirmwareVersion):
            msgBox = QMessageBox(self)
            msgBox.setText(_translate("Dialog","The Tonino firmware is outdated!",None))
            msgBox.setInformativeText(_translate("Dialog","Do you want to update to %s?",None)%self.version2str(self.app.included_firmware_version))
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Ok)
            ret = msgBox.exec_()
            if ret == QMessageBox.Ok:
                self.updateFirmware()


    def disconnectTonino(self,onStartup=False):
        self.app.ser.closePort()
        self.app.toninoPort = None
        self.app.toninoFirmwareVersion = None
        self.setEnabledUI(False)
        self.showMessage(_translate("Message","Not connected",None))
        if not onStartup:
            self.app.scales.setDeviceCoefficients(None)
        self.deviceCheckInterval = self.fastCheck
        self.deviceCheckCounter = 0
        
    def connectTonino(self,port,version):
        self.app.toninoPort = port
        self.app.toninoFirmwareVersion = version
        self.setEnabledUI(True)
        self.showMessage(_translate("Message","Connected to Tonino",None) + " " + self.version2str(version))
        try:
            self.app.scales.setDeviceCoefficients(self.app.getScale(port))
        except:
            self.showMessage(_translate("Message","Scale could not be retrieved",None) + " " + self.version2str(version))
        self.deviceCheckInterval = self.slowCheck
        self.checkFirmwareVersion()

    # checks regular for connect or disconnect of a Tonino device
    # on first call, the self.ports list is initialized, all other calls compare the list of ports with that one
    def deviceCheck(self):
        newports = self.app.ser.getSerialPorts()
        res = None
        if self.ports == None:
            # we just started up, check if there is already a Tonino connected we can attach too
                if newports:
                    res = self.checkPorts(newports,True)
        else:
            # in case ports were detected before
            if self.toninoConnected():
                # a Tonino was already connected before
                if not self.app.toninoPort in newports:
                    # Tonino port disappeared
                    self.disconnectTonino()
            else:
                # test if any of the new ports is connected to a Tonino
                res = self.checkPorts(list(set(newports) - set(self.ports)))
        # update serial ports
        self.ports = newports
        # connect if version was returned
        if res:
            (port,version) = res
            self.connectTonino(port,version)
        
        # increment decay counter
        self.deviceCheckCounter = self.deviceCheckCounter + 1

        # register next shot        
        if self.deviceCheckCounter > self.checkDecay:
            # turn to slowCheck
            self.deviceCheckInterval = self.slowCheck
        QTimer.singleShot(self.deviceCheckInterval,self.deviceCheck)
        
    def setEnabledUI(self,state):
        self.ui.pushButtonDefaults.setEnabled(state)
        self.ui.pushButtonAdd.setEnabled(state)
        self.ui.pushButtonCalib.setEnabled(state)
        self.setEnabledUploadButton()
        
    def setEnabledUploadButton(self):
        self.ui.pushButtonUpload.setEnabled(bool(self.app.toninoPort and self.app.scales.getCoefficients()))

    # returns True if action should be continued else False
    def verifyDirty(self):
        if self.app.currentFileDirty:
            msgBox = QMessageBox(self)
            msgBox.setText(_translate("Dialog","The scale has been modified.",None))
            msgBox.setInformativeText(_translate("Dialog","Do you want to save your changes?",None))
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            ret = msgBox.exec_()
            if ret == QMessageBox.Save:
                self.saveFile()
                return True
            elif ret == QMessageBox.Cancel:
                return False
            else:
                return True
        else:
            return True
    
    def closeEvent(self,event):
        self.app.saveSettings()
        if self.verifyDirty():
            event.accept()
        else:
            event.ignore()

###########################################################################################################################################

def main():
    # define app
    app = Tonino(sys.argv)
    app.setApplicationName("Tonino")                  #needed by QSettings() to store windows geometry in operating system
    app.setOrganizationName("BottledSense")           #needed by QSettings() to store windows geometry in operating system
    app.setOrganizationDomain("my-tonino.com")        #needed by QSettings() to store windows geometry in operating system 
    if platform.system() == 'Windows':
        app.setWindowIcon(QIcon("tonino.png"))
        if resources.main_is_frozen():
            try:
                sys.stderr = sys.stdout
            except:
                pass
        
        
    if platform.system() == 'Darwin':
        import objc
        from Cocoa import NSUserDefaults
        defs = NSUserDefaults.standardUserDefaults() 
        langs = defs.objectForKey_("AppleLanguages")
        lang = langs.objectAtIndex_(0)
    else:
        lang = QLocale.system().name()[:2]
    
    # load localization
    translator = QTranslator(app)
    if translator.load("tonino_" + lang + ".qm",resources.getTranslationsPath()):
        app.installTranslator(translator)        
    translator = QTranslator(app)  
    if translator.load("qt_" + lang + ".qm",resources.getSystemTranslationsPath()):
        app.installTranslator(translator)
    
    aw = ApplicationWindow(app=app)
    aw.show()
    
    # load Tonino scale on double click a *.toni file in the Finder while Tonino.app is not yet running
    try:
        if sys.argv and len(sys.argv) > 1:
            aw.loadFile(sys.argv[1])
    except Exception:
        pass
    
    # start the Tonino discovery process
    aw.deviceCheck()
    
    #the following line is to trap numpy warnings
    with numpy.errstate(invalid='ignore'):
        sys.exit(app.exec_())
