#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# serialport.py
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

import serial  # @UnusedImport
import serial.tools.list_ports
import time
import platform
import logging
from typing import Final

_log: Final = logging.getLogger(__name__)

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
        _log.debug("configurePort: %s",port)
        self.port = port
        if platform.system() == 'Windows':
            self.SP.setDTR(False)
            _log.debug("setDTR(False)")
        self.SP.port = self.port
        self.SP.baudrate = self.baudrate
        self.SP.bytesize = self.bytesize
        self.SP.parity = self.parity
        self.SP.stopbits = self.stopbits
        self.SP.timeout = self.timeout
        _log.debug("baudrate: %s",self.baudrate)
        _log.debug("bytesize: %s",self.bytesize)
        _log.debug("parity: %s",self.parity)
        _log.debug("stopbits: %s",self.stopbits)
        _log.debug("timeout: %s",self.timeout) 

    def openPort(self,port):
        _log.debug("openPort(%s)",port)
        try:
            if self.port != None and port != self.port:
                self.closePort()
            if not self.SP.isOpen():
                # open port if not yet open
                self.configurePort(port)
                self.SP.open()
                time.sleep(.1) # avoid possible hickups on startup
        except serial.SerialException as e:
            _log.exception(e)
            self.closePort()
    
    def closePort(self):
        _log.debug("closePort")
        try:
            self.port = None
            self.SP.close()
            time.sleep(0.7) # on OS X opening a serial port too fast after closing the port get's disabled
        except Exception as e:  # pylint: disable=broad-except
            _log.exception(e)
            
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
        except Exception as e:  # pylint: disable=broad-except
            _log.exception(e)
            self.closePort()
            return None
        
    def sendCommand(self,port,command,retry=True):
        _log.debug("sendCommand(%s,%s,%s)",port,command,retry)
        res = None
        if not self.SP.isOpen():
            self.openPort(port)
        try:
            if self.SP.isOpen():
                self.SP.flushInput() # needed to avoid to interpret leftovers from the buffer
                self.SP.flushOutput()
                self.SP.write(str2cmd("\n" + command + "\n"))
                self.SP.flush()
                time.sleep(0.3)
                r = self.SP.readline()
                response = cmd2str(r)
                _log.debug("response(%s): %s",len(response),response.strip())
                if not (response and len(response) > 0):
                    # we got an empty line, maybe the next line contains the response
                    r = self.SP.readline()
                    response = cmd2str(r)
                    _log.debug("second response(%s):%s",len(response),response.strip())
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
                _log.debug("result: %s",res)
                return res
        except Exception as e:  # pylint: disable=broad-except
            _log.exception(e)
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
#        classicToninoProduct = "VID_0403\+PID_6001"
        classicToninoPID = 24577 # 6001 (hex)
        # TinyTonino model (1)
#        tinyToninoProduct = "VID_0403\+PID_6015" 
        tinyToninoPID = 24597 # 6015 (hex)
        if platform.system() == 'Windows':
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
            except Exception as e:  # pylint: disable=broad-except
                _log.exception(e)
