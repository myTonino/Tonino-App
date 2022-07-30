#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# main.py
#
# Copyright (c) 2022, Paul Holleis, Marko Luther
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

import warnings

# filter warning in py2app/pyinstaller builds: "The MATPLOTLIBDATA environment variable was deprecated in Matplotlib 3.1 and will be removed in 3.3. "
#warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)

import sys
import os
import platform
import json
import time
import numpy as np
from functools import reduce as freduce
import numpy.polynomial.polynomial as poly
import scipy.stats

import logging.config
from yaml import safe_load as yaml_load
from typing import Final

try: # activate support for hiDPI screens on Windows
    if str(platform.system()).startswith('Windows'):
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
        os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'
except Exception: # pylint: disable=broad-except
    pass    
    
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QMessageBox, QFileDialog, QProgressDialog, QDialogButtonBox, QInputDialog)
from PyQt6.QtGui import (QAction, QIcon, QFont)
from PyQt6.QtCore import (QProcess, QTimer, QSettings, QLocale, QTranslator, QDir, QFileInfo, QEvent, Qt, pyqtSignal, QItemSelection, QItemSelectionModel, pyqtSlot)


from lib import __version__
import lib.serialport
import lib.scales
from uic import MainWindowUI, AboutDialogUI, PreferencesDialogUI, CalibDialogUI, TinyCalibDialogUI, TinyCalibDialogUI2, DebugDialogUI, PreCalibDialogUI
import uic.resources as resources


try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

def u(x): # convert to unicode string
    return str(x)

## to make py2exe happy with scipy >0.11
#def __dependencies_for_freezing():
#    from scipy.sparse.csgraph import _validation  # @UnusedImport
#    from scipy.special import _ufuncs_cxx  # @UnusedImport
##    from scipy import integrate
##    from scipy import interpolate
#    # to make bbfreeze on Linux happy with scipy > 0.17.0
#    import scipy.linalg.cython_blas  # @UnusedImport
#    import scipy.linalg.cython_lapack  # @UnusedImport
#    import pydoc
#    
##    import appdirs  # @UnusedImport
#    import packaging  # @UnusedImport
#    import packaging.version  # @UnusedImport
#    import packaging.specifiers  # @UnusedImport
#    import packaging.markers  # @UnusedImport
#    import packaging.requirements  # @UnusedImport
#    
##    import PyQt5.QtSvg  # @UnusedImport
##    import PyQt5.QtXml  # @UnusedImport
##    import PyQt5.QtDBus   # @UnusedImport # needed for QT5 builds
##    import PyQt5.QtPrintSupport   # @UnusedImport # needed for by platform plugin libqcocoa
#
#del __dependencies_for_freezing


_log: Final = logging.getLogger(__name__)

###########################################################################################################################################
#
# Tonino Application
#
 
class Tonino(QApplication):
    def __init__(self, arguments):
        super(Tonino, self).__init__(arguments)
        self.aw = None
        
        # constants
        self.tonino_model = 0 # 0: Classic Tonino (@115200 baud); 1: Tiny Tonino (@57600 baud)
        if platform.system() == 'Windows':
            self.avrdude = "avrdude.exe"
        else:
            self.avrdude = "avrdude"
        self.avrdude_conf = "avrdude.conf"
        # ClassicTonino firmware (v1.x.x)
        self.included_firmware_name = None
        self.included_firmware_version = None # a list of three int indicating major, minor and build versions of the included firmware
        # TinyTonino firmware (v2.x.x)
        self.included_tinyTonino_firmware_name = None
        self.included_tinyTonino_firmware_version = None # a list of three int indicating major, minor and build versions of the included firmware
        
        # calib constants
        self.calib_dark_scan = False # dark readings are already taken on scan by the TinyTonino device!
        self.clib_double_scan = False
        
        ### NOTE: the calib target and range values are reset by the function setModel below!!!
        # setup for the Classic Tonino (this will be updated dynamically based on the model of the connected Tonino in setModel())
        self.std_calib_low_r = 2600. # brown disk red reading
        self.std_calib_low_b = 1600. # brown disk blue reading
        self.std_calib_high_r = 15000. # red disk red reading
        self.std_calib_high_b = 3600. # red disk blue reading

        # calib targets (reset by setModel() based on model and firmwarer version !!)
        self.std_calib_target_low = 1.5
        self.std_calib_target_high = 3.7
        
        # the tolerance distance of the calib measurements to the expected values above that still allow the recognition
        self.std_calib_low_r_range = 2000 # brown disk red reading range 
        self.std_calib_low_b_range = 1300 # brown disk blue reading range
        self.std_calib_high_r_range = 6500 # red disk red reading range 
        self.std_calib_high_b_range = 2000 # red disk blue reading range
        
        # r/b Tiny calibration targets and ranges
        self.tiny_low_rb = 1.49 # green disk r/b target
        self.tiny_high_rb = 3.07 # red disk r/b target
        self.tiny_rb_range_low = 0.15 # green disk r/b range
        self.tiny_rb_range_high = 0.27 # red disk r/b range
        
        # variables
        self.workingDirectory = None
        self.currentFile = None
        self.currentFileDirty = False # should be cleared on save and set on any modification
        self.maxRecentFiles = 10
        self.recentFiles = []
        
        self.pre_cal_targets = [] # pre calibration targets for the classic r/b ratio formula usind in firmware v2 and v3 for recognizing the calib disk
        self.pre_cal_cardinality = 4 # number of required source and target readings
        self.pre_cal_degree = 2 # quadratic
        
        self.serialStringMaxLength = 50
        self.paramSeparatorChar = " " # separator char used by the Tonino serial protocol
        self.toninoPort = None # port of the connected Tonino
        self.toninoFirmwareVersion = [] # a list of three int indicating major, minor and build versions of the connected device
        self.toninoControllerType = None # the type of the Tonino micro controller (Arduino Nano, Micro,..)
        self.scales = lib.scales.Scales(self,self)
        self.ser = lib.serialport.SerialPort() # the serial connection object
        # calibration raw readings
        self.calib_low_r = None
        self.calib_low_b = None
        self.calib_high_r = None
        self.calib_high_b = None
        self.retrieveIncludedFirmware()

    def setModel(self,model):
        self.tonino_model = model
        if self.tonino_model == 0:
            # for the Classic Tonino
            self.std_calib_target_low = 1.5
            self.std_calib_target_high = 3.7
            # --
            self.std_calib_low_r = 2600. # brown disk red reading
            self.std_calib_low_b = 1600. # brown disk blue reading
            self.std_calib_high_r = 15000. # red disk red reading
            self.std_calib_high_b = 3600. # red disk blue reading
            # --
            self.std_calib_low_r_range = 2100 # brown disk red reading rang
            self.std_calib_low_b_range = 1500 # brown disk blue reading range 
            self.std_calib_high_r_range = 7000 # red disk red reading range 
            self.std_calib_high_b_range = 2100 # red disk blue reading range
        else:
            # for the Tiny Tonino
            self.std_calib_target_low = 1.316187404
            self.std_calib_target_high = 2.873957082
            # --
            self.std_calib_low_r = 27600. # green disk red reading
            self.std_calib_low_b = 18800. # green disk blue reading
            self.std_calib_high_r = 34890. # red disk red reading
            self.std_calib_high_b = 11500. # red disk blue reading
            # --
            self.std_calib_low_r_range = 5000 # green disk red reading range
            self.std_calib_low_b_range = 3600 # green disk blue reading range
            self.std_calib_high_r_range = 5300 # red disk red reading range
            self.std_calib_high_b_range = 2500 # red disk blue reading range
        
    def getModel(self):
        return self.tonino_model
      
    def clearCalibReadings(self):
        self.calib_low_r = None
        self.calib_low_b = None
        self.calib_high_r = None
        self.calib_high_b = None
        
    # detects if the given red and blue readings are in the range of either the low or the high calibration disk
    # and sets the corresponding variables accordingly
    def setCalibReadings(self,r,b):
        rb = r/float(b)
        if self.tonino_model:
            # TinyTonino
            if abs(rb-self.tiny_low_rb) < self.tiny_rb_range_low:
                # calib_low disk recognized
                self.calib_low_r = r
                self.calib_low_b = b
                _log.debug("setCalibReadings(%s,%s): TinyTonino LOW",r,b)
            elif abs(rb-self.tiny_high_rb) < self.tiny_rb_range_high:
                # calib_high disk recognized
                self.calib_high_r = r
                self.calib_high_b = b
                _log.debug("setCalibReadings(%s,%s): TinyTonino HIGH",r,b)
        else:
            # ClassicTonino
            if abs(r - self.std_calib_low_r) < self.std_calib_low_r_range and abs(b - self.std_calib_low_b) < self.std_calib_low_b_range:
                # calib_low disk recognized
                self.calib_low_r = r
                self.calib_low_b = b
                _log.debug("setCalibReadings(%s,%s): ClassicTonino LOW",r,b)
            elif abs(r - self.std_calib_high_r) < self.std_calib_high_r_range and abs(b - self.std_calib_high_b) < self.std_calib_high_b_range:
                # calib_high disk recognized
                self.calib_high_r = r
                self.calib_high_b = b
                _log.debug("setCalibReadings(%s,%s): ClassicTonino HEIGH",r,b)
            
    def getCalibLow(self):
        if self.calib_low_r and self.calib_low_b:
            return (self.calib_low_r,self.calib_low_b)
        else:
            return None
            
    def getCalibHigh(self):
        if self.calib_high_r and self.calib_high_b:
            return (self.calib_high_r,self.calib_high_b)
        else:
            return None

    def updateCalib(self):
        _log.info("updateCalib")
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
        _log.debug("retrieveIncludedFirmware")
        qd = QDir()
        qd.setCurrent(resources.getResourcePath())
        # retrieve included Classic Tonino firmware version
        fileinfos = qd.entryInfoList(["tonino-*.hex"],QDir.Filter.Files | QDir.Filter.Readable,QDir.SortFlag.Name | QDir.SortFlag.Reversed)
        if len(fileinfos) > 0:
            fn = fileinfos[0].fileName()
            try:
                self.included_firmware_version = [int(s) for s in fn.split("-")[1].rsplit(".")[:3]]
                self.included_firmware_name = fn
            except Exception as ex: # pylint: disable=broad-except
                _log.exception(ex)
        # retrieve included Classic Tonino firmware version
        fileinfos = qd.entryInfoList(["tinyTonino-*.hex"],QDir.Filter.Files | QDir.Filter.Readable,QDir.SortFlag.Name | QDir.SortFlag.Reversed)
        if len(fileinfos) > 0:
            fn = fileinfos[0].fileName()
            try:
                self.included_tinyTonino_firmware_version = [int(s) for s in fn.split("-")[1].rsplit(".")[:3]]
                self.included_tinyTonino_firmware_name = fn
            except Exception as ef: # pylint: disable=broad-except
                _log.exception(ef)
        
    # returns True if version v1 is greater than v2 and False otherwise and if the arguments are malformed
    def versionGT(self,v1,v2):
        if v1 is not None and v2 is not None and len(v1) == len(v2) == 3:
            for i in range(3):
                if v1[i] > v2[i]:
                    return True
                elif v1[i] < v2[i]:
                    return False
            return False
        return False
                
    
    # load Tonino configuration on double click a *.toni file in the Finder while Tonino.app is already running
    def event(self, event):
        if event.type() == QEvent.Type.FileOpen:
            try:
                self.aw.loadFile(event.file())
            except Exception as e: # pylint: disable=broad-except
                _log.exception(e)
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
                self.app.resetsettings = settings.value("resetsettings",self.app.resetsettings).toInt()[0]
                if self.app.resetsettings:
                    self.app.resetsettings = 0
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
            if settings.contains("recentFiles"):
                self.recentFiles = settings.value("recentFiles")
            if settings.contains("preCalTargets"):
                self.pre_cal_targets = [float(f) for f in settings.value("preCalTargets",self.pre_cal_targets)]
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
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
            # pre calib targets
            settings.setValue("preCalTargets",self.pre_cal_targets)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.app.resetsettings = 0 # ensure that the corrupt settings are not loaded on next start and thus overwritten
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
        
    def toString(self,o):
        if sys.version < '3':
            return str(o)
        else:
            if type(o) == bytes:
                return str(o,"latin1")
            else:
                return str(o)
                
    def float2str(self,max_len,n):
        if n == int(n):
            return '%d'%n
        else:
            li = len(str(int(n))) + 1 # of characters for decimal point + preceding numbers
            return ('{number:.{digits}f}'.format(number=n, digits=max(0,max_len-li))).rstrip('0').rstrip('.')

    # format given float numbers into a string of maximal total_size (plus additional space in-between)
    # trying to give as many digits as possible per number
    def floats2str(self,total_size,numbers):
        chars_per_number = int(total_size / len(numbers))
        res = ""
        left_over_chars = 0
        for n in numbers:
            n_str = self.float2str(chars_per_number+left_over_chars,n)
            left_over_chars += chars_per_number - len(n_str)
            res = res + n_str + self.paramSeparatorChar
        return res[:-1]
  
    # if fitStringMaxLength=True, values are assumed to be floats which are rendered to fit in a string of total_size characters + (n-1)*separator_chars
    def formatCommand(self,cmd,values,onSend=True,fitStringMaxLength=False):
        if fitStringMaxLength:
            prefix = cmd + (" " if onSend else ":")
            return prefix + self.floats2str(self.serialStringMaxLength - len(prefix) - (len(values)-1),values)
        else:
            return cmd + (" " if onSend else ":") + self.paramSeparatorChar + self.paramSeparatorChar.join([self.toString(v) for v in values])
            
    
    def resetArduino(self):
        if self.toninoPort:
            self.ser.sendReset(self.toninoPort)
 
    def uploadFirmware(self):
        _log.info("uploadFirmware")
        resourcePath = resources.getResourcePath()
        resourceBinaryPath = resources.getResourceBinaryPath()
        avrdude = resourceBinaryPath + self.avrdude
        avrdudeconf = resourceBinaryPath + self.avrdude_conf
        if self.getModel() == 1:
            # TinyTonino firmware
            toninoSketch = resourcePath + self.included_tinyTonino_firmware_name
        else:
            # ClassicTonino firmware
            toninoSketch = resourcePath + self.included_firmware_name
        ags = ["-C",avrdudeconf,"-q","-q","-patmega328p","-carduino","-P",self.toninoPort,"-b57600","-D","-Uflash:w:" + u(toninoSketch) + ":i"]
        # -s : Disable safemode prompting
        # -V : Disable automatic verify check when uploading data
        # -v : Enable verbose output. More -v options increase verbosity level.
        # -q : Disable (or quell) output of the progress bar while reading or writing to the device. Specify it a second time for even quieter operation.
        # -l : logfile
        # -F : Ignore signature check
        _log.debug("averdude: %s",avrdude)
        _log.debug("args: %s",ags)
        
        process = QProcess(self)
        process.finished.connect(self.uploadFirmwareDone)
        process.start(avrdude,ags)
        self.aw.showprogress.emit()
    
    @pyqtSlot(int,"QProcess::ExitStatus")
    def uploadFirmwareDone(self,exitCode,_exitStatus):
        _log.info("uploadFirmwareDone")
        if exitCode:
            # update failed
            self.aw.showMessage(_translate("Message","Firmware update failed",None),msecs=10000)
        else:
            self.aw.showMessage(_translate("Message","Firmware successfully updated",None),msecs=10000)
        self.aw.endprogress.emit()
        time.sleep(2)
        
    # requests version string from connected Tonino
    # returns None if communication fails and the version object (a list of three integers: major, minor, build) otherwise
    # cmd: TONINO
    # onStartup should be true if this is the first check after app start    
    def getToninoFirmwareVersion(self,port,onStartup=False):
        _log.debug("getToninoFirmwareVersion(%s,%s)",port,onStartup)
        res = None
        if port:
            # send "TONINO" to the given serial port and returns the successful parsed version as int list
            # [major,minor,build]
            if onStartup:
                time.sleep(.1) # if device is already connected it should be already starting up
            else:
                time.sleep(.8) # wait a moment until the Arduino allows to open the port and finished its serial device init
            try:
                self.ser.openPort(port) # on macOS this will trigger an Arduino reset
            except Exception as e: # pylint: disable=broad-except
                _log.exception(e)
            if onStartup:
                time.sleep(2.5)  # wait a second until the Arduino Nano did a reset
            else:
                time.sleep(2)  # wait a second until the Arduino Nano did a reset
#            self.ser.sendCommand(port,"",False) # first send a dummy empty cmd to get serial started # NOTE: this seems not to be neccessary any longer
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
                res = self.response2values(response,int,1)[0]
        return res
    
    # cmd: SETBRIGHTNESS (0-15)
    def setDisplayBrightness(self,port,brightness):
        if port:
            self.ser.sendCommand(port,self.formatCommand("SETBRIGHTNESS",[brightness]))

    # cmd: GETTARGET
    def getTarget(self,port):
        res = None
        if port:
            response = self.ser.sendCommand(port,"GETTARGET")
            if response:
                res = self.response2values(response,int,2)
        return res
    
    # cmd: SETTARGET (value: 0-200 / range: 0-10)
    def setTarget(self,port,value,range_):
        if port:
            self.ser.sendCommand(port,self.formatCommand("SETTARGET",[value,range_]))
            
    # cmd: GETSCALE
    def getScaleName(self,port):
        res = None
        if port:
            response = self.ser.sendCommand(port,"GETSCALE")
            if response:
                res = self.response2values(response,str,1)[0]
        return res
    
    # cmd: SETSCALE (a string of length 8)
    def setScaleName(self,port,name):
        if port:
            self.ser.sendCommand(port,self.formatCommand("SETSCALE",[u(name[:8]).encode('ascii', 'ignore')]))
            
    # cmd: GETNAME
    def getUserName(self,port):
        res = None
        if port:
            response = self.ser.sendCommand(port,"GETNAME")
            if response:
                res = self.response2values(response,str,1)[0]
        return res
    
    # cmd: SETNAME (a string of length 8)
    def setUserName(self,port,name):
        if port:
            self.ser.sendCommand(port,self.formatCommand("SETNAME",[u(name[:8]).encode('ascii', 'ignore')]))
            
    # cmd: GETDFLIP
    def getDisplayFlip(self,port):
        res = None
        if port:
            response = self.ser.sendCommand(port,"GETDFLIP")
            if response:
                res = self.response2values(response,int,1)[0]
        return res
    
    # cmd: SETDFLIP (a string of length 8)
    def setSetDisplayFlip(self,port,flipFlag):
        if port:
            if flipFlag:
                value = 1
            else:
                value = 0
            self.ser.sendCommand(port,self.formatCommand("SETDFLIP",[value]))
                    
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
            self.ser.sendCommand(port,self.formatCommand("SETSCALING",scaling, fitStringMaxLength=True))
        
    # cmd: SETCAL
    def setCal(self,port,cal):
        if port:
            self.ser.sendCommand(port,self.formatCommand("SETCAL",cal, fitStringMaxLength=True))
        
    # cmd: I_SCAN (calibrated r/b)
    def getRawCalibratedReading(self,port):
        res = None
        response = self.ser.sendCommand(port,"I_SCAN")
        if response:
            res = self.response2values(response,float,1)
        return res

    # cmd: II_SCAN (pre-calibrated readings)
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
                _log.info("loadScale(%s))",filename)
                return True
            else:
                return False
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            if self.aw:
                QMessageBox.critical(self.aw,_translate("Message", "Error",None),_translate("Message", "Scale could not be loaded",None))
            return False
        
    # write current scale to file
    # returns True if saving suceeded
    def saveScale(self,filename):
        try:
            cs = self.scales.getScale()
            if cs:
                outfile = open(filename, 'w', encoding='utf-8')
                json.dump(cs, outfile, ensure_ascii=True)
                outfile.write('\n')
                outfile.close()
                self.contentCleared()
                _log.info("saveScale(%s))",filename)
                return True
            else:
                return False
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
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
            self.aw.updateLCDS()
            _log.info("applyScale(%s))",filename)
            return True
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
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
        self.aw.updateLCDS()
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

    def keyPressEvent(self,event):
        key = int(event.key())
        if key == 16777216: #ESCAPE
            self.close()
            
class PreferencesDialog(ToninoDialog):
    def __init__(self, parent = None, application=None):
        super(PreferencesDialog,self).__init__(parent)        
        self.app = application
        self.ui = PreferencesDialogUI.Ui_Preferences()
        self.ui.setupUi(self)
        self.displayBrightness = None
        self.targetValue = None
        self.targetRange = None
        self.userName = None
        self.displayFlip = None
        if self.app.toninoPort:
            try:
                self.displayBrightness = self.app.getDisplayBrightness(self.app.toninoPort)
                self.ui.displaySlider.setValue(self.displayBrightness)
            except Exception as e: # pylint: disable=broad-except
                _log.exception(e)
            if self.app.getModel() == 1: # TinyTonino
                try:
                    v = self.app.getTarget(self.app.toninoPort)
                    self.targetValue = v[0]
                    self.targetRange = v[1]
                    self.ui.targetValueSpinBox.setValue(self.targetValue)
                    self.ui.rangeSlider.setValue(self.targetRange)
                    self.userName = self.app.getUserName(self.app.toninoPort)
                    self.ui.lineEditName.setText(self.userName)
                    self.displayFlip = self.app.getDisplayFlip(self.app.toninoPort)
                    if self.displayFlip:
                        self.ui.checkBoxFlip.setChecked(True)
                    else:
                        self.ui.checkBoxFlip.setChecked(False)
                        
                except Exception as e: # pylint: disable=broad-except
                    _log.exception(e)
                
            else: # Classic Tonino
                self.ui.groupBoxToninoTarget.setEnabled(False)
                self.ui.groupBoxToninoName.setEnabled(False)
                self.ui.checkBoxFlip.setEnabled(False)
        else: # not connected
            self.ui.groupBoxToninoDisplay.setEnabled(False)
            self.ui.groupBoxToninoTarget.setEnabled(False)
            self.ui.groupBoxToninoName.setEnabled(False)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        
        self.ui.displaySlider.setTracking(False) # no valueChanged signals while moving
        self.ui.displaySlider.valueChanged.connect(self.displaySliderChanged)


    @pyqtSlot(int)
    def displaySliderChanged(self,_=0):
        v = self.ui.displaySlider.value()
        if self.displayBrightness is not None and self.displayBrightness != v:
            self.app.setDisplayBrightness(self.app.toninoPort,v)

    @pyqtSlot()
    def accept(self):
        try:
            v = self.ui.targetValueSpinBox.value()
            r = self.ui.rangeSlider.value()
            if not (self.targetValue and self.targetRange and self.targetValue == v and self.targetRange == r):
                # target values have been changed, we write them back to the device
                self.app.setTarget(self.app.toninoPort,v,r)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
        try:
            n = self.ui.lineEditName.text()
            if not (self.userName and self.userName == n):
                # user name has been changed, we write it back to the device
                self.app.setUserName(self.app.toninoPort,n)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
        try:
            if self.ui.checkBoxFlip.isChecked():
                f = 1
            else:
                f = 0
            if not (self.displayFlip and self.displayFlip == f):
                self.app.setSetDisplayFlip(self.app.toninoPort,f)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
        self.done(0)
    
    @pyqtSlot()
    def reject(self):
        self.app.setDisplayBrightness(self.app.toninoPort,self.displayBrightness)
        self.done(0)
    
    def close(self):
        self.reject()

class CalibDialog(ToninoDialog):
    def __init__(self, parent = None, application=None):
        super(CalibDialog,self).__init__(parent)
        self.setModal(True)
        self.app = application
        if app.tonino_model == 0: # Classic Tonino
            self.ui = CalibDialogUI.Ui_Dialog()
        else: # Tiny Tonino
            if app.toninoFirmwareVersion and len(app.toninoFirmwareVersion) > 2 and (app.toninoFirmwareVersion[0] > 2 or app.toninoFirmwareVersion[1] > 0):
                # from v2.1.0 on the red disk is the one to start calibration
                self.ui = TinyCalibDialogUI2.Ui_Dialog()
            else:
                self.ui = TinyCalibDialogUI.Ui_Dialog()
        self.ui.setupUi(self)
        
        # disable elements
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).repaint()
        self.ui.calibLowLabel.setEnabled(False)
        self.ui.calibHighLabel.setEnabled(False)
        # connect actions
        self.ui.pushButtonScan.clicked.connect(self.scan)
        # clear previous calibrations
        self.app.clearCalibReadings()

    @pyqtSlot(bool)
    def scan(self,_=False):
        try:
            raw_readings1 = self.app.getRawReadings(self.app.toninoPort)
            if self.app.calib_dark_scan:
                time.sleep(.75)
                dark_readings = self.app.getBlackReadings(self.app.toninoPort)
            else:
                dark_readings = None            
            if self.app.clib_double_scan:        
                time.sleep(.75)
                raw_readings2 = self.app.getRawReadings(self.app.toninoPort)
            else:
                raw_readings2 = None
            if raw_readings1 == None:
                raw_readings1 = raw_readings2
            if raw_readings2 == None:
                raw_readings2 = raw_readings1
            if dark_readings == None:
                dark_readings = [0., 0., 0., 0.]
            if raw_readings1 and raw_readings2 and dark_readings and len(raw_readings1)>3 and len(raw_readings2)>3 and len(dark_readings)>3:
                r = (raw_readings1[1] + raw_readings2[1]) / 2. - dark_readings[1]
                b = (raw_readings1[3] + raw_readings2[3]) / 2. - dark_readings[3]
                self.app.setCalibReadings(r,b)
                calib_low = self.app.getCalibLow()
                calib_high = self.app.getCalibHigh()
                # if low reading is set enable the calib_low
                if calib_low:
                    self.ui.calibLowLabel.setEnabled(True)
                    self.ui.calibLowLabel.repaint()
                if calib_high:
                    self.ui.calibHighLabel.setEnabled(True)
                    self.ui.calibHighLabel.repaint()
                # if both, low and high readings are set, enable the OK button  
                if calib_low and calib_high:
                    self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
                    self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).repaint() # on some Qt/PyQt 5.x versions the button is not automatically repainted!
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
        
    def accept(self):
        self.app.updateCalib()
        self.done(0)
        
    def reject(self):
        self.done(0)
    
    def close(self):
        self.reject()

###########################################################################################################################################

class DebugDialog(ToninoDialog):
    def __init__(self, parent = None, application=None):
        super(DebugDialog,self).__init__(parent)
        self.setModal(True)
        self.app = application
        self.ui = DebugDialogUI.Ui_Dialog()
        self.ui.setupUi(self)
        # connect actions
        self.ui.pushButtonScan.clicked.connect(self.scan)
        # prepare log
        #self.ui.logOutput.setReadOnly(True)
        # disable elements
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).repaint()
        self.ui.pushButtonScan.setEnabled(False)
        self.ui.pushButtonScan.repaint()
        QTimer.singleShot(0, self.insertSettings)
        
    def insertSettings(self):
        self.ui.logOutput.appendPlainText("<Settings>")
        self.app.processEvents()      
        self.insertRequestResponse("TONINO")
        self.app.processEvents()
        self.insertRequestResponse("GETSCALING")
        self.app.processEvents()
        self.insertRequestResponse("GETBRIGHTNESS")
        self.app.processEvents()
        if self.app.getModel() == 0: 
            # followings are only supported by the Classic Tonino:
            self.insertRequestResponse("GETCAL")
            self.app.processEvents()
            self.insertRequestResponse("GETSAMPLING")
            self.app.processEvents()
            self.insertRequestResponse("GETCMODE")
            self.app.processEvents()
            self.insertRequestResponse("GETLTDELAY")
            self.app.processEvents()
            self.insertRequestResponse("GETCALINIT")
            self.app.processEvents()
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).repaint()
        self.ui.pushButtonScan.setEnabled(True)
        self.ui.pushButtonScan.repaint()

    def insertRequestResponse(self,cmd):
        try:
            res = self.app.ser.sendCommand(self.app.toninoPort,cmd)
            self.ui.logOutput.appendPlainText(cmd + ":" + res)
            self.ui.logOutput.repaint()
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.ui.logOutput.appendPlainText(cmd + ": failed")
            self.ui.logOutput.appendPlainText("  " + str(e))     
            self.ui.logOutput.repaint()

    @pyqtSlot(bool)
    def scan(self,_=False):
        try:
            self.ui.logOutput.appendPlainText("<Scan>")
            self.insertRequestResponse("II_SCAN")
            self.insertRequestResponse("D_SCAN")
            self.ui.logOutput.repaint()
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.ui.logOutput.appendPlainText("  " + str(e))
            self.ui.logOutput.repaint()
        
    def accept(self):
        self.done(0)
        
    def reject(self):
        self.done(0)
    
    def close(self):
        self.reject()

###########################################################################################################################################

class PreCalibDialog(ToninoDialog):
    def __init__(self, parent = None, application=None):
        super(PreCalibDialog,self).__init__(parent)
        self.setModal(True)
        self.app = application
        self.ui = PreCalibDialogUI.Ui_Dialog()
        self.ui.setupUi(self)
        # connect actions
        self.ui.pushButtonMaster.clicked.connect(self.master)
        self.ui.pushButtonScan.clicked.connect(self.scan)
        self.ui.pushButtonPreCal.clicked.connect(self.preCal)
        self.ui.pushButtonSet.clicked.connect(self.set)
        self.ui.pushButtonReset.clicked.connect(self.reset)
        # prepare log
        #self.ui.logOutput.setReadOnly(True)
        # disable elements
        if len(self.app.pre_cal_targets) != self.app.pre_cal_cardinality:
            self.ui.pushButtonScan.setEnabled(False)
            self.ui.pushButtonScan.repaint()
        self.ui.pushButtonPreCal.setEnabled(False)
        self.ui.pushButtonPreCal.repaint()
        self.sources = [] # r/b source ratios for the pre-calibration
        self.ui.logOutput.appendPlainText("targets: ")
        targets_str = ""
        for t in self.app.pre_cal_targets:
            targets_str = targets_str + str(t).replace(".",",") + " "
        self.ui.logOutput.appendPlainText(targets_str[:-1])
        self.ui.logOutput.repaint()

    def insertRequestResponse(self,cmd):
        try:
            res = self.app.ser.sendCommand(self.app.toninoPort,cmd)
            self.ui.logOutput.appendPlainText(cmd + ":" + res)
            self.ui.logOutput.repaint()
            return res
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.ui.logOutput.appendPlainText(cmd + ": failed")
            self.ui.logOutput.appendPlainText("  " + str(e))
            self.ui.logOutput.repaint()

    @pyqtSlot(bool)
    def master(self,_=False):
        try:
            if len(self.app.pre_cal_targets) >= self.app.pre_cal_cardinality:
                self.app.pre_cal_targets = [] # we start over
                self.ui.pushButtonScan.setEnabled(False)
                self.ui.pushButtonScan.repaint()
            self.ui.logOutput.appendPlainText("<Master>")
            res = self.insertRequestResponse("RSCAN") # RSCAN
            if res:
                res = self.app.response2values(res,float,5)
                if len(res) == 5:
                    self.app.pre_cal_targets.append(res[1]/res[3]) # append classic r/b ratio
                self.ui.logOutput.appendPlainText("targets r/b: " + str(["{0:.3f}".format(t) for t in self.app.pre_cal_targets]))
            if len(self.app.pre_cal_targets) == self.app.pre_cal_cardinality:
                self.ui.pushButtonScan.setEnabled(True)
                self.ui.pushButtonScan.repaint()
            self.ui.logOutput.repaint()
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.ui.logOutput.appendPlainText("  " + str(e)) 
            self.ui.logOutput.repaint()

    @pyqtSlot(bool)
    def scan(self,_=False):
        try:
            if len(self.sources) == self.app.pre_cal_cardinality:
                self.sources = [] # we start over
                self.ui.pushButtonPreCal.setEnabled(False)
                self.ui.pushButtonPreCal.repaint()
            self.ui.logOutput.appendPlainText("<Scan>")
            res = self.insertRequestResponse("RSCAN") # RSCAN
            if res:
                res = self.app.response2values(res,float,5)
                if len(res) == 5:
                    self.sources.append(res[1]/res[3])
                self.ui.logOutput.appendPlainText("sources: " + str(["{0:.3f}".format(t) for t in self.sources]))
            if len(self.sources) == self.app.pre_cal_cardinality:
                self.ui.pushButtonPreCal.setEnabled(True)
                self.ui.pushButtonPreCal.repaint()
            self.ui.logOutput.repaint()
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.ui.logOutput.appendPlainText("  " + str(e)) 
            self.ui.logOutput.repaint()
            
    @pyqtSlot(bool)
    def preCal(self,_=False):
        try:
            self.ui.logOutput.appendPlainText("<PreCal>")
            c,_ = poly.polyfit(self.sources,self.app.pre_cal_targets,self.app.pre_cal_degree,full=True)
            coefficients = list(c)
            coefficients.reverse()
            coefs = ""
            coefficients = [0]*(max(0,3-len(coefficients))) + coefficients
            for c in coefficients[-3:]:
                coefs = coefs + str(c).replace(".",",") + " "
            self.ui.logOutput.appendPlainText("coefficients:")
            self.ui.logOutput.appendPlainText(coefs[:-1])
            self.ui.logOutput.repaint()
            self.app.ser.sendCommand(self.app.toninoPort,self.app.formatCommand("SETPRE",coefficients,fitStringMaxLength=True))
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.ui.logOutput.appendPlainText("  " + str(e))
            self.ui.logOutput.repaint()

    @pyqtSlot(bool)
    def set(self,_=False):
        try:
            self.ui.logOutput.appendPlainText("<Set>")
            text, ok = QInputDialog.getText(self, 'Set Pre-Calibration', 'Enter pre-calibration triple:')
            if ok:
                line = str(text)
                line = line.replace("\t"," ").replace(",",".")
                self.ui.logOutput.appendPlainText("coefficients:")
                self.ui.logOutput.appendPlainText(line)
                self.ui.logOutput.repaint()
                values = line.split(" ")
                values = [float(v) for v in values]
                self.app.ser.sendCommand(self.app.toninoPort,self.app.formatCommand("SETPRE",values,fitStringMaxLength=True))
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.ui.logOutput.appendPlainText("  " + str(e))
            self.ui.logOutput.repaint()
    
    @pyqtSlot(bool)
    def reset(self,_=False):
        try:
            self.ui.logOutput.appendPlainText("<Reset>")
            self.ui.logOutput.appendPlainText("coefficients:")
            self.ui.logOutput.appendPlainText("0 1 0")
            self.ui.logOutput.repaint()
            self.app.ser.sendCommand(self.app.toninoPort,self.app.formatCommand("SETPRE",[0,1,0]))
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.ui.logOutput.appendPlainText("  " + str(e))
            self.ui.logOutput.repaint()
        
        
    def accept(self):
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
    
    def __init__(self, parent=None,application=None):
        super(QMainWindow, self).__init__(parent)
        self.app = application
        self.ui = MainWindowUI.Ui_MainWindow()
        self.ui.setupUi(self)
        self.app.aw = self
        
        self.calibs = None
        self.debugDialog = None
        self.preCalibDialog = None
        
        self.closing = False # set to True if app is closing down
        
        # reinitialize QAbstractTable model to ensure the tables parent is initialized to the main window
        self.app.scales = lib.scales.Scales(self.app,self)

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
        self.debug = 0 # toggled via a right-click / Control-click (macOS) on the About dialog
            # 0: debug off
            # 1: debug on (calib replaced by debug & newer firmware versions can be replaced by older)
            # 2: debug on + no communication before firmware upgrade (upgrade starts immediately on connect; forced update)
        self.debug_logging = 0 # 0: debug logging disabled; 1: debug logging enabled
            # toggled via a right-click + Option / Control-Option-click (macOS) on the About dialog
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
        self.ui.pushButtonAdd.clicked.connect(self.addCoordinateSlot)
        self.ui.pushButtonDelete.clicked.connect(self.deleteCoordinates)
        self.ui.pushButtonClear.clicked.connect(self.clearCoordinates)
        self.ui.pushButtonSort.clicked.connect(self.sortCoordinates)
        self.ui.pushButtonCalib.clicked.connect(self.showDebugOrCalib)
        self.ui.degreeSlider.setTracking(False) # no valueChanged signals while moving
        self.ui.degreeSlider.valueChanged.connect(self.sliderChanged)
        self.ui.actionCut.triggered.connect(self.actionCut)
        self.ui.actionCopy.triggered.connect(self.actionCopy)
        self.ui.actionPaste.triggered.connect(self.actionPaste)
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.pushButtonUpload.setEnabled(False)
        self.ui.pushButtonUpload.repaint()
        
        # enable buttons
        self.ui.pushButtonDelete.setEnabled(False)
        self.ui.pushButtonDelete.repaint()

        
        # initalize dirty state
        self.app.contentCleared()
        
        # move slider
        self.ui.degreeSlider.setValue(self.app.scales.getPolyfitDegree())
        
        # connect coordinates table view to model
        self.ui.tableView.setModel(self.app.scales)
        self.ui.tableView.setColumnWidth(0,50)
        self.ui.tableView.setItemDelegate(lib.scales.ValidatedItemDelegate(self.ui.tableView))
        
#        self.ui.tableView.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,QSizePolicy.Policy.MinimumExpanding)
        
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
        
        self.updateLCDS()
        
        _log.info("initalized")

    @pyqtSlot(bool)
    def actionCut(self,_=False):
        try:
            self.actionCopy()
            self.deleteCoordinates()
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)

    @pyqtSlot(bool)
    def actionCopy(self,_=False):
        try:
            clipboard = QApplication.clipboard()
            selected = self.app.scales.getSelectedCoordinates()
            selected_text = self.app.scales.coordinates2text(selected)
            clipboard.setText(selected_text)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)

    @pyqtSlot(bool)
    def actionPaste(self,_=False):
        try:
            clipboard = QApplication.clipboard()
            self.app.scales.addCoordinates(self.app.scales.text2coordinates(clipboard.text()))
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
    
    @pyqtSlot()
    def showProgress(self):
        self.progress = QProgressDialog(_translate("Message","Updating firmware...",None), None, 0, 20, self)
        self.progress.setCancelButton(None)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setAutoClose(False)
        self.progress.show()
        # this try-except is needed as after the "if self.progress" and before the access, 
        # the endProgress() might have set self.progress to None already and then the access crashes the app!
        try: 
            for i in range(20):
                if self.progress:
                    self.progress.setValue(i)
                time.sleep(1)
            if self.progress:
                self.progress.setRange(0,0)
                self.progress.setValue(0)
                self.progress.show()
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
        
    @pyqtSlot()
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
            if path is None:   
                path = self.app.getWorkingDirectory()
            if openFile:
                res = QFileDialog.getOpenFileName(self,msg,path,ffilter)
            else:
                res = QFileDialog.getSaveFileName(self,msg,path,ffilter)

            if res is not None and res != "":
                if isinstance(res,list) or isinstance(res,tuple):
                    res = res[0]
                self.app.setWorkingDirectory(res)
            return res
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
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
            if self.app.recentFiles is None:
                self.app.recentFiles = []
            try:
                self.app.recentFiles = list(filter((filename).__ne__, self.app.recentFiles))
            except Exception as e: # pylint: disable=broad-except
                _log.exception(e)
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
                self.app.recentFiles.insert(0, filename)
                del self.app.recentFiles[self.app.maxRecentFiles:]
                self.updateRecentFileActions()
           
    @pyqtSlot(bool)
    def openFile(self,_=False):
        self.loadFile(self.fileDialog(_translate("Dialog","Open Scale",None),ffilter=self.toninoFileFilter))
        
    def openRecent(self):
        action = self.sender()
        if action:
            self.loadFile(action.data())
    
    # returns True if saving suceeded and was not canceled
    @pyqtSlot(bool)
    def saveFile(self,_=False):
        currentFile = self.app.currentFile
        if currentFile:
            _log.debug("saveFile")
            self.app.saveScale(currentFile)
            self.setCurrentFile(currentFile)
            return True
        else:
            return self.saveAsFile()
        
    # returns True if saving suceeded and was not canceled
    def saveAsFile(self):
        filename = self.fileDialog(_translate("Dialog","Save As",None),ffilter=self.toninoFileFilter,openFile=False)
        if filename:
            if not filename.endswith("." + self.toninoFileExtension):
                filename = filename + "." + self.toninoFileExtension
            res = self.app.saveScale(filename)
            if res:
                self.setCurrentFile(filename)
                self.updateWindowTitle()
                _log.debug("saveAsFile(%s)",filename)
                return True
            else:
                return False
        else:
            return False
    
    @pyqtSlot(bool)
    def applyFile(self,_=False):
        _log.debug("applyFile")
        self.applyScale(self.fileDialog(_translate("Dialog","Apply Scale",None),ffilter=self.toninoFileFilter))
        
    def applyRecent(self):
        action = self.sender()
        if action:
            _log.debug("applyRecent")
            self.applyScale(action.data())

#
# Buttons
#

    @pyqtSlot(bool)
    def defaults(self,_=False):
        _log.info("defaults")
        self.app.reset2Defaults(self.app.toninoPort)
        self.app.scales.setDeviceCoefficients(self.app.getScale(self.app.toninoPort))
        self.showMessage(_translate("Message","Tonino reset to defaults",None))
    
    @pyqtSlot(bool)
    def uploadScale(self,_=False):
        if self.app.toninoPort and self.app.scales.getCoefficients():
            scale = self.app.scales.getCoefficients()
            scale = [0.]*(4-len(scale)) + scale # ensure a 4 element scale
            self.app.setScale(self.app.toninoPort,scale)
            self.app.scales.setDeviceCoefficients(self.app.getScale(self.app.toninoPort))
            if self.app.currentFile and self.app.getModel() == 1:
                scaleName = self.app.strippedName(self.app.currentFile).split(".")[0]
                self.app.setScaleName(self.app.toninoPort,scaleName)
            self.showMessage(_translate("Message","Scale uploaded",None))
            
    @pyqtSlot(bool)
    def addCoordinateSlot(self,_=False):
        self.addCoordinate(True)
    
    def addCoordinate(self,retry=True):
        try:
            raw_x = self.app.getRawCalibratedReading(self.app.toninoPort)
            if raw_x:
                if np.isnan(raw_x[0]) or raw_x[0] == float('inf'):
                    self.showMessage(_translate("Message","Coordinate out of range",None),msecs=10000)
                else:
                    self.app.scales.addCoordinate(raw_x[0],None)
                    self.ui.widget.canvas.repaint()
                    QTimer.singleShot(0, self.ui.tableView.scrollToBottom)
            else:
                if retry:
                    self.addCoordinate(retry=False)
                    self.ui.widget.canvas.repaint()
                else:
                    self.showMessage(_translate("Message","Coordinate out of range",None),msecs=10000)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)

    @pyqtSlot(bool)
    def deleteCoordinates(self,_=False):
        _log.debug("deleteCoordinates")
        self.app.scales.deleteCoordinates([s.row() for s in self.ui.tableView.selectionModel().selectedRows()])
        self.ui.widget.canvas.repaint()
        
    @pyqtSlot(bool)
    def clearCoordinates(self,_=False):
        _log.debug("clearCoordinates")
        self.app.scales.clearCoordinates()
        self.ui.widget.canvas.repaint()
        self.updateLCDS()
        
    @pyqtSlot(bool)
    def sortCoordinates(self,_=False):
        _log.debug("sortCoordinates")
        self.app.scales.sortCoordinates()
        self.ui.widget.canvas.repaint()
        
#
# Slider
#

    @pyqtSlot(int)
    def sliderChanged(self,_=0):
        self.app.scales.setPolyfitDegree(self.ui.degreeSlider.value())
        self.ui.widget.canvas.repaint()
        self.updateLCDS()
        _log.debug("sliderChanged(%s)",self.ui.degreeSlider.value())

    
#
# Measurements Table
#        


    def mean_confidence_interval(self,data, confidence=0.95):
        a = 1.0*np.array(data)
        n = len(a)
        _, se = np.mean(a), scipy.stats.sem(a)
#        h = se * scipy.stats.t._ppf((1+confidence)/2., n-1)
        h = se * scipy.stats.t.ppf((1+confidence)/2., n-1)
        return h
    
    def updateLCDS(self):
        try:
            if self.ui and self.ui.tableView and self.ui.tableView.selectionModel() and self.ui.tableView.selectionModel().selectedRows():
                coordinates = self.app.scales.getSelectedCoordinates()
            else:
                coordinates = []
            values = [self.app.scales.computeT(x[0]) for x in coordinates]
            self.updateAVG(values)
            self.updateSTDEV(values)
            self.updateCONF(values)
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)

    def updateAVG(self, values):
        if values and len(values) > 0:
            avg = sum(values) / float(len(values))
            self.ui.LCDavg.display("%.1f" % avg)
        else:
            self.ui.LCDavg.display("")
        self.ui.LCDavg.repaint()
            
    def updateSTDEV(self, values):
        if values and len(values) > 1:
            stdev = np.std(np.array(values),dtype=np.float64)
            self.ui.LCDstdev.display("%.1f" % stdev)
        else:
            self.ui.LCDstdev.display("")
        self.ui.LCDstdev.repaint()
            
    def updateCONF(self, values):
        if values and len(values) > 1:
            self.ui.LCDconf.display("%.2f" % self.mean_confidence_interval(values))
        else:
            self.ui.LCDconf.display("")
        self.ui.LCDconf.repaint()
        
    @pyqtSlot("QItemSelection","QItemSelection")
    def selectionChanged(self, _newSelection, _oldSelection):
        self.updateLCDS()
        if self.ui.tableView.selectionModel().selectedRows():
            self.ui.pushButtonDelete.setEnabled(True)
            self.ui.pushButtonDelete.repaint()
        else:
            self.ui.pushButtonDelete.setEnabled(False)
            self.ui.pushButtonDelete.repaint()
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
            QItemSelectionModel.SelectionFlag.Toggle)
        
        
#
# Dialogs
#
    @pyqtSlot(bool)
    def showAboutQt(self,_=False):
        _log.debug("showAboutQt")
        QApplication.instance().aboutQt()
        
    @pyqtSlot(bool)
    def showAbout(self,_=False):
        _log.debug("showAbout")
        Dialog = QDialog(self)
        ui = AboutDialogUI.Ui_Dialog()
        ui.setupUi(Dialog)
        version = _translate("Dialog", "Version", None) + " " + __version__
        if self.app.included_firmware_version or self.app.included_tinyTonino_firmware_version:
            version += " (firmware "
            if self.app.included_firmware_version:
                version += self.version2str(self.app.included_firmware_version,prefix="")
            if self.app.included_firmware_version and self.app.included_tinyTonino_firmware_version:
                version += "/"
            if self.app.included_tinyTonino_firmware_version:
                version += self.version2str(self.app.included_tinyTonino_firmware_version,prefix="")
            version += ")"
        ui.versionLabel.setText(version)
        ui.pushButton.clicked.connect(Dialog.accept)
        Dialog.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        Dialog.customContextMenuRequested.connect(lambda _: self.toggleDebug(ui))
        if self.debug == 1:
            ui.nameLabel.setText(_translate("Dialog", "Tonino*", None))
        elif self.debug == 2:
            ui.nameLabel.setText(_translate("Dialog", "Tonino**", None))
        Dialog.show()
    
    def toggleDebug(self,ui):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.MetaModifier|Qt.KeyboardModifier.AltModifier:
            self.toggleDebugLogging()
        else:
            self.debug = (self.debug + 1) % 3
            if self.debug == 1:
                ui.nameLabel.setText(_translate("Dialog", "Tonino*", None))
                _log.info("debug: Tonino*")
            elif self.debug == 2:
                ui.nameLabel.setText(_translate("Dialog", "Tonino**", None))
                _log.info("debug: Tonino**")
            else:
                ui.nameLabel.setText(_translate("Dialog", "Tonino", None))
                _log.info("debug: Tonino")
    
    def toggleDebugLogging(self):
        self.debug_logging = (self.debug_logging + 1) % 2
        if self.debug_logging:
            level = logging.DEBUG
            self.showMessage(_translate("Message","debug logging ON",None),msecs=3000)
        else:
            level = logging.INFO
            self.showMessage(_translate("Message","debug logging OFF",None),msecs=3000)
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict if ('.' not in name)]  # @UndefinedVariable pylint: disable=no-member
        for logger in loggers:
            logger.setLevel(level)
            for handler in logger.handlers:
                if handler.get_name() == 'file':
                    handler.setLevel(level)
        
    @pyqtSlot(bool)
    def showPreferences(self,_=False):
        _log.debug("showPreferences")
        prefs = PreferencesDialog(self,self.app)
        prefs.show()
        
    @pyqtSlot(bool)
    def showDebugOrCalib(self,_=False):
        _log.debug("showDebugOrCalib")
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            self.showPreCalib()
            #self.app.preCalibration(self.app.toninoPort)
        else:
            if self.debug:
                self.showDebug()
            else:
                self.showCalib()
        
    def showCalib(self):
        _log.debug("showCalib")
        self.calibs = CalibDialog(self,self.app)
        self.calibs.show()
        
    def showDebug(self):
        _log.debug("showDebug")
        self.debugDialog = DebugDialog(self,self.app)
        self.debugDialog.show()
        
    def showPreCalib(self):
        _log.debug("showPreCalib")
        self.preCalibDialog = PreCalibDialog(self,self.app)
        self.preCalibDialog.show()
        
        
#
# Firmware Update
#                   
            
    def updateFirmware(self):
        _log.info("updateFirmware")
        if self.app.toninoPort:
            # disconnect established serial connection
            self.app.ser.closePort()
#        self.app.resetArduino() # not needed as done by the avrdude cmd
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
                    _log.debug("port: %s",p)
                    _log.debug("firmware version: %s",version)
                    res = p,version
                    break
        return res


    def showMessage(self,s,msecs=0):
        _log.info("message: %s",s)
        self.ui.status.showMessage(s,msecs)
        self.ui.status.repaint()
        
    def toninoConnected(self):
        return self.app.toninoPort

    def checkFirmwareVersion(self):
        _log.debug("checkFirmwareVersion")
        if self.app.getModel() == 1:
            firmware_version = self.app.included_tinyTonino_firmware_version
        else:
            firmware_version = self.app.included_firmware_version
        if self.debug or (self.app.versionGT(firmware_version,self.app.toninoFirmwareVersion) and firmware_version[0] == self.app.toninoFirmwareVersion[0]):
            # ask to update if the installed firmware version has the same major version as the latest firmware version included in the app and is older
            msgBox = QMessageBox(self)
            msgBox.setText(_translate("Dialog","The Tonino firmware is outdated!",None))
            msgBox.setInformativeText(_translate("Dialog","Do you want to update to %s?",None)%self.version2str(firmware_version))
            msgBox.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            msgBox.setDefaultButton(QMessageBox.StandardButton.Ok)
            ret = msgBox.exec()
            if ret == QMessageBox.StandardButton.Ok:
                if self.debug == 2:
                    self.debug = 0
                self.updateFirmware()


    def disconnectTonino(self,onStartup=False):
        _log.info("disconnectTonino(%s)",onStartup)
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
        _log.info("connectTonino(%s,%s)",port,version)
        self.app.toninoPort = port
        self.app.toninoFirmwareVersion = version
        # we update the Tonino model based on the new finds
        self.app.setModel(self.app.ser.getModel())
        self.setEnabledUI(True)
        if self.app.getModel() == 0:
            self.showMessage(_translate("Message","Connected to Tonino",None) + " " + self.version2str(version))
        else:
            self.showMessage(_translate("Message","Connected to TinyTonino",None) + " " + self.version2str(version))
        try:
            self.app.scales.setDeviceCoefficients(self.app.getScale(port))
        except Exception as e: # pylint: disable=broad-except
            _log.exception(e)
            self.showMessage(_translate("Message","Scale could not be retrieved",None) + " " + self.version2str(version))
        self.deviceCheckInterval = self.slowCheck
        self.checkFirmwareVersion()

    # checks regular for connect or disconnect of a Tonino device
    # on first call, the self.ports list is initialized, all other calls compare the list of ports with that one
    def deviceCheck(self):
        newports = self.app.ser.getSerialPorts()
        res = None
        if self.ports is None:
            # we just started up, check if there is already a Tonino connected we can attach too
            if newports:
                res = self.checkPorts(newports,True)
                if res:
                    model = self.app.ser.getModel()
                    self.app.setModel(model)
                    if model == 0:
                        _log.debug("ClassicTonino detected: %s",res)
                    else:
                        _log.debug("TinyTonino detected: %s",res)
        else:
            # in case ports were detected before
            if self.toninoConnected():
                # a Tonino was already connected before
                if not self.app.toninoPort in newports:
                    # Tonino port disappeared
                    self.disconnectTonino()
            else:
                new_ports = list(set(newports) - set(self.ports))
                if self.debug == 2 and new_ports:                    
                    self.app.toninoPort = new_ports[0]
                    self.checkFirmwareVersion()
                else:
                    # test if any of the new ports is connected to a Tonino
                    res = self.checkPorts(new_ports)
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
        self.ui.pushButtonDefaults.repaint()
        self.ui.pushButtonAdd.setEnabled(state)
        self.ui.pushButtonAdd.repaint()
        self.ui.pushButtonCalib.setEnabled(state)
        self.ui.pushButtonCalib.repaint()
        self.setEnabledUploadButton()
        
    def setEnabledUploadButton(self):
        self.ui.pushButtonUpload.setEnabled(bool(self.app.toninoPort and self.app.scales.getCoefficients()))
        self.ui.pushButtonUpload.repaint()

    # returns True if action should be continued else False
    def verifyDirty(self):
        if self.app.currentFileDirty:
            msgBox = QMessageBox(self)
            msgBox.setText(_translate("Dialog","The scale has been modified.",None))
            msgBox.setInformativeText(_translate("Dialog","Do you want to save your changes?",None))
            msgBox.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            msgBox.setDefaultButton(QMessageBox.StandardButton.Save)
            ret = msgBox.exec()
            if ret == QMessageBox.StandardButton.Save:
                return self.saveFile()
            elif ret == QMessageBox.StandardButton.Cancel:
                return False
            else:
                self.app.currentFileDirty = False
                return True
        else:
            return True
    
    @pyqtSlot(bool)
    def close(self,_=False):    
        self.closeEvent(None)
        
    def closeEvent(self,event):
        if self.closing or self.verifyDirty():
            if not self.closing:
                self.app.saveSettings()
                self.app.ser.closePort()
            self.closing = True
            if event:
                event.accept()
            else:
                QApplication.exit()
        else:
            if event:
                event.ignore()
            else:
                QApplication.exit()
        

###########################################################################################################################################


# suppress all warnings
warnings.filterwarnings('ignore')

aw = None # this is to ensure that the variable aw is already defined during application initialization


try:
    vv, _, _ = platform.mac_ver()
    vv = vv.split('.')[:2]
    major = int(vv[0])
    minor = int(vv[1])
    if major >= 10 and minor >= 10: #v >= 10.10:
        # fix Mac OS X 10.10 (Yosemite) font issue
        # https://bugreports.qt-project.org/browse/QTBUG-40833
        QFont.insertSubstitution(".Helvetica Neue DeskInterface", "Helvetica Neue")
    if major >= 10 and minor >= 9: #v >= 10.9:
        # fix Mac OS X 10.9 (mavericks) font issue
        # https://bugreports.qt-project.org/browse/QTBUG-32789
        QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")
except Exception as es: # pylint: disable=broad-except
    _log.exception(es)

# define app
args = sys.argv
if sys.platform == 'linux' :
    # avoid a GTK bug in Ubuntu Unity
    args = args + ['-style','Cleanlooks']
app = Tonino(args)
app.setApplicationName("Tonino")                  #needed by QSettings() to store windows geometry in operating system
app.setOrganizationName("myTonino")           #needed by QSettings() to store windows geometry in operating system
app.setOrganizationDomain("my-tonino.com")        #needed by QSettings() to store windows geometry in operating system 
if platform.system() == 'Windows':
    app.setWindowIcon(QIcon("tonino.png"))
    if resources.main_is_frozen():
        try:
            sys.stderr = sys.stdout
        except Exception: # pylint: disable=broad-except
            pass

# configure logging
try:
    with open(os.path.join(resources.getResourcePath(),'logging.yaml'), encoding='utf-8') as logging_conf:
        conf = yaml_load(logging_conf)
        try:
            # set log file to Tonino data directory
            conf['handlers']['file']['filename'] = os.path.join(resources.getDataDirectory(),'tonino.log')
        except Exception: # pylint: disable=broad-except
            pass
        logging.config.dictConfig(conf)
except Exception: # pylint: disable=broad-except
    pass

_log.info(
    '%s v%s',
    'Tonino',
    str(__version__)
)
     
    
if platform.system() == 'Darwin':
    import objc  # @UnusedImport
    from Cocoa import NSUserDefaults  # @UnresolvedImport
    defs = NSUserDefaults.standardUserDefaults() 
    langs = defs.objectForKey_("AppleLanguages")
    if langs.objectAtIndex_(0)[:3] == "zh_" or langs.objectAtIndex_(0)[:3] == "pt_":
        lang = langs.objectAtIndex_(0)[:5]
    else:
        lang = langs.objectAtIndex_(0)[:2]        
else:
    lang = QLocale.system().name()[:2]

# load localization
translator = QTranslator(app)
if translator.load("tonino_" + lang + ".qm",resources.getTranslationsPath()):
    app.installTranslator(translator)        
translator = QTranslator(app)  
if translator.load("qt_" + lang + ".qm",resources.getSystemTranslationsPath()):
    app.installTranslator(translator)

aw = ApplicationWindow(application=app)
aw.show()

# load Tonino scale on double click a *.toni file in the Finder while Tonino.app is not yet running
try:
    if sys.argv and len(sys.argv) > 1:
        aw.loadFile(sys.argv[1])
except Exception as et: # pylint: disable=broad-except
    _log.exception(et)

# start the Tonino discovery process
QTimer.singleShot(aw.deviceCheckInterval,aw.deviceCheck)
    
