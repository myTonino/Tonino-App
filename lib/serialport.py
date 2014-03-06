#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# serialport.py
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

import serial.tools.list_ports
import time
import sys
import os
import platform

# on OS X load the Makerbot modified list_ports module patched for P3k
# we still keep this hack under pyserial 2.7 as it does not work as expected on Python3 (reporting an empty port list always)
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
        return bytes(s,"ascii")
    def cmd2str(c):
        return str(c,"latin1")
        
class SerialPort(object):
    def __init__(self):
        self.port = None
        self.baudrate = 115200
        self.bytesize = serial.EIGHTBITS
        self.parity= serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 1.7
        self.SP = serial.Serial(rtscts=0, dsrdtr=0)
        self.SP = serial.Serial()
        self.cmdSeparatorChar = ":"
        
    #loads configuration to ports
    def configurePort(self,port):
        self.port = port
        self.SP.setPort(self.port)
        self.SP.setBaudrate(self.baudrate)
        self.SP.setByteSize(self.bytesize)
        self.SP.setParity(self.parity)
        self.SP.setStopbits(self.stopbits)
        self.SP.setTimeout(self.timeout)
        if platform.system() == 'Windows':
            self.SP.setDTR(False)

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
            self.SP.close()
    
    def closePort(self):
        try:
            self.port = None
            self.SP.close()
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
                if not (response and len(response) > 0):
                    # we got an empty line, maybe the next line contains the response
                    r = self.SP.readline()
                    response = cmd2str(r)
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
            self.closePort()
            if retry:
                return self.sendCommand(port,command,False)
            else:
                return None
            
    def getSerialPorts(self):
        if platform.system() == 'Windows':
            # only connected FTDI FT232R products (VID=403(hex), PID=6001) are returned
            return list(p[0] for p in serial.tools.list_ports.grep("VID_0403\+PID_6001"))
        else:
            ports = serial.tools.list_ports.comports()
            # only connected FTDI FT232R products (VID=403(hex), PID=6001) are returned
            # TODO: this might crash on Linux (test!)
            return list(p['port'] for p in filter_ports_by_vid_pid(ports,vid=1027,pid=24577))
        
    def sendReset(self,port):
        if not self.SP.isOpen():
            self.openPort(port)
        try:
            if self.SP.isOpen():
                self.SP.setDTR(0)
                time.sleep(0.1)
                self.SP.setDTR(1)
                self.closePort()
        except:
            self.closePort()
