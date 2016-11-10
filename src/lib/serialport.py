#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# serialport.py
#
# Copyright (c) 2016, Paul Holleis, Marko Luther
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

import serial
import serial.tools.list_ports
import time
import sys
import os
import platform

# on OS X load the Makerbot modified list_ports module patched for P3k
# we still keep this hack under pyserial 2.7 as it does not work as expected on Python3 (reporting an empty port list always)

#   list_ports module patched for P3k from new pyserial GitHub repository
if serial.VERSION.split(".")[0].strip() == "2":
    if sys.platform == 'darwin':
        from lib.list_ports_osx import comports
        serial.tools.list_ports.comports = comports
        from lib.list_ports_vid_pid_osx_posix import *
    elif os.name == 'posix':
        from lib.list_ports_vid_pid_osx_posix import *

if sys.version < '3':
    def str2cmd(s):
        return s
    def cmd2str(c):
        return c
else:
    def str2cmd(s):
        if type(s) == bytes:
            return s
        else:
            return bytes(s,"ascii")
    def cmd2str(c):
        if type(c) == bytes:
        	return str(c,"latin1")
        else:
            return c
        
class SerialPort(object):
    def __init__(self,model=0):
        self.port = None
        self.model = None
        self.setModel(model) # set model and correspoding baudrate
        self.baudrate = 115200
        self.bytesize = serial.EIGHTBITS
        self.parity= serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 1.7
        self.SP = serial.Serial(rtscts=0, dsrdtr=0)
        self.SP = serial.Serial()
        self.cmdSeparatorChar = ":"
        
    def setModel(self,model=0):
        self.model = model
        if self.model == 1:
            # Tiny Tonino
            self.baudrate = 57600
        else: 
            # Classic Tonino
            self.baudrate = 115200
            
    def getModel(self):
        return self.model
        
    #loads configuration to ports
    def configurePort(self,port):
        self.port = port
        if platform.system() == 'Windows':
            self.SP.setDTR(False)
        if serial.VERSION.split(".")[0].strip() == "2":
            self.SP.setPort(self.port)
            self.SP.setBaudrate(self.baudrate)
            self.SP.setByteSize(self.bytesize)
            self.SP.setParity(self.parity)
            self.SP.setStopbits(self.stopbits)
            self.SP.setTimeout(self.timeout)
        else:
            self.SP.port = self.port
            self.SP.baudrate = self.baudrate
            self.SP.bytesize = self.bytesize
            self.SP.parity = self.parity
            self.SP.stopbits = self.stopbits
            self.SP.timeout = self.timeout

    def openPort(self,port):
        try:
            if port != self.port:
                self.closePort()
            if not self.SP.isOpen():
                # open port if not yet open
                self.configurePort(port)
                self.SP.open()
                time.sleep(.1) # avoid possible hickups on startup
        except serial.SerialException:
            self.closePort()
    
    def closePort(self):
        try:
            self.port = None
            self.SP.close()
            time.sleep(0.7) # on OS X opening a serial port too fast after closing the port get's disabled
        except:
            pass
            
    def writeString(self,port,s):
        if not self.SP.isOpen():
            self.openPort(port)
        try:
            if self.SP.isOpen():
                self.SP.flushInput()
                self.SP.flushOutput()
                self.SP.write(str2cmd(s + "\n"))
                self.SP.flush()
                return cmd2str(self.SP.readline())
            else:
                return None
        except:
            self.closePort()
            return None
        
    def sendCommand(self,port,command,retry=True):
#        print("sendCommand",port,command,retry,self.baudrate)
        res = None
        if not self.SP.isOpen():
            self.openPort(port)
        try:
            if self.SP.isOpen():
                self.SP.flushInput()
                self.SP.flushOutput()
                self.SP.write(str2cmd("\n" + command + "\n"))
                self.SP.flush()
                time.sleep(0.3)
                r = self.SP.readline()
                response = cmd2str(r)
#                print("response",len(response),response)
                if not (response and len(response) > 0):
                    # we got an empty line, maybe the next line contains the response
                    r = self.SP.readline()
                    response = cmd2str(r)
#                    print("second response",len(response),response)
                if response and len(response) > 0:
                    # each <command> is answered by the Tonino by returning "<command>:<result>\n"
                    parts = response.split(command + self.cmdSeparatorChar)
                    if parts and len(parts) == 2:
                        res = parts[1].strip()
                    elif parts and len(parts) == 1:
                        res = ""
            if retry and res == None:
                return self.sendCommand(port,command,False)
            else:
                return res
        except:
#            print("exception")
            self.closePort()
            if retry:
                return self.sendCommand(port,command,False)
            else:
                return None
            
    def getSerialPorts(self):
        # we are looking for 
        #   Classic Tonino: VID 403(hex)/1027(dec) and PID 6001(hex)/24577(dec)
        #      Tiny Tonino: VID 403(hex)/1027(dec) and PID 6015(hex)/24597(dec)
        vid = 1027 # 403 (hex)
        # ClassicTonino model (0)
        classicToninoProduct = "VID_0403\+PID_6001"
        classicToninoPID = 24577 # 6001 (hex)
        # TinyTonino model (1)
        tinyToninoProduct = "VID_0403\+PID_6015"
        tinyToninoPID = 24597 # 6015 (hex)
        if platform.system() == 'Windows':
            if serial.VERSION.split(".")[0].strip() == "2":
                tinyToninos = list(p[0] for p in serial.tools.list_ports.grep(tinyToninoProduct))
                if tinyToninos and len(tinyToninos) > 0:
                    self.setModel(1)
                    return tinyToninos
                else:
                    self.setModel(0)
                    return list(p[0] for p in serial.tools.list_ports.grep(classicToninoProduct))
            else:
                # pyserial >2.7
                ports = list(serial.tools.list_ports.comports())
                tinyToninos = list(self.filter_ports_by_vid_pid(ports,vid,tinyToninoPID))
                if tinyToninos and len(tinyToninos) > 0:
                    self.setModel(1)
                    return tinyToninos
                else:
                    self.setModel(0)
                    return list(self.filter_ports_by_vid_pid(ports,vid,classicToninoPID))
        else:
            if serial.VERSION.split(".")[0].strip() == "2":
                # pyserial v2.7 version
                ports = list(serial.tools.list_ports.comports())
                tinyToninos = list(p['port'] for p in filter_ports_by_vid_pid(ports,vid=vid,pid=tinyToninoPID))
                if tinyToninos and len(tinyToninos) > 0:
                    self.setModel(1)
                    return tinyToninos
                else:
                    self.setModel(0)
                    return list(p['port'] for p in filter_ports_by_vid_pid(ports,vid=vid,pid=classicToninoPID))
            else:
                # pyserial >2.7
                ports = list(serial.tools.list_ports.comports())
                tinyToninos = list(self.filter_ports_by_vid_pid(ports,vid,tinyToninoPID))
                if tinyToninos and len(tinyToninos) > 0:
                    self.setModel(1)
                    return tinyToninos
                else:
                    self.setModel(0)
                    return list(self.filter_ports_by_vid_pid(ports,vid,classicToninoPID))
            
    def filter_ports_by_vid_pid(self,ports,vid=None,pid=None):
        """ Given a VID and PID value, scans for available port, and
    	f matches are found, returns a dict of 'VID/PID/iSerial/Port'
    	that have those values.
    
        @param list ports: Ports object of valid ports
        @param int vid: The VID value for a port
        @param int pid: The PID value for a port
        @return iterator: Ports that are currently active with these VID/PID values
        """
        for port in ports:
            #Parse some info out of the identifier string
            try: 
                if vid == None or port.vid == vid:
                    if pid == None or  port.pid == pid:
                        yield port.device
            except:
                pass
