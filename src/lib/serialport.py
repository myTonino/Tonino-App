#!/usr/bin/python
#
# serialport.py
#
# Copyright (c) 2023, Paul Holleis, Marko Luther
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
from typing import Optional, Final, Union, Iterator, cast

_log: Final = logging.getLogger(__name__)

def str2cmd(s:Union[str,bytes]) -> bytes:
    if type(s) == bytes:
        return s
    return bytes(cast(str,s),'ascii')

def cmd2str(c:Union[str,bytes]) -> str:
    if type(c) == bytes:
        return str(c,'latin1')
    return cast(str,c)

class SerialPort:
    def __init__(self,model:int=0) -> None:
        self.port:Optional[str] = None
        self.model:Optional[int] = None # 1: TinyTonino, 0: Classic Tonino, None otherwise
        self.setModel(model) # set model and correspoding baudrate
        self.baudrate:int = 115200
        self.bytesize:int = serial.EIGHTBITS
        self.parity:str = serial.PARITY_NONE
        self.stopbits:int = serial.STOPBITS_ONE
        self.timeout:float = 1.7
        self.SP:serial.Serial = serial.Serial()
        self.cmdSeparatorChar:str = ':'

    def setModel(self,model:Optional[int]=0) -> None:
        self.model = model
        if self.model == 1:
            # Tiny Tonino
            self.baudrate = 57600
        else:
            # Classic Tonino
            self.baudrate = 115200

    def getModel(self) -> Optional[int]:
        return self.model

    #loads configuration to ports
    def configurePort(self,port:str) -> None:
        _log.debug('configurePort: %s',port)
        self.port = port
        if platform.system() == 'Windows':
            self.SP.setDTR(False) # type: ignore
            _log.debug('setDTR(False)')
        self.SP.port = self.port
        self.SP.baudrate = self.baudrate
        self.SP.bytesize = self.bytesize
        self.SP.parity = self.parity
        self.SP.stopbits = self.stopbits
        self.SP.timeout = self.timeout
        _log.debug('baudrate: %s',self.baudrate)
        _log.debug('bytesize: %s',self.bytesize)
        _log.debug('parity: %s',self.parity)
        _log.debug('stopbits: %s',self.stopbits)
        _log.debug('timeout: %s',self.timeout)

    def openPort(self,port:str) -> None:
        _log.debug('openPort(%s)',port)
        try:
            if self.port != None and port != self.port:
                self.closePort()
            if not self.SP.is_open:
                # open port if not yet open
                self.configurePort(port)
                self.SP.open()
                time.sleep(.1) # avoid possible hickups on startup
        except serial.SerialException as e:
            _log.exception(e)
            self.closePort()

    def closePort(self) -> None:
        _log.debug('closePort')
        try:
            self.port = None
            self.SP.close()
            time.sleep(0.7) # on OS X opening a serial port too fast after closing the port get's disabled
        except Exception as e:  # pylint: disable=broad-except
            _log.exception(e)

    def writeString(self,port:str, s:str) -> Optional[str]:
        if not self.SP.is_open:
            self.openPort(port)
        try:
            if self.SP.is_open:
                self.SP.reset_input_buffer()
                self.SP.reset_output_buffer()
                self.SP.write(str2cmd(s + '\n'))
                self.SP.flush()
                return cmd2str(self.SP.readline())
            else:
                return None
        except Exception as e:  # pylint: disable=broad-except
            _log.exception(e)
            self.closePort()
            return None

    def sendCommand(self,port:str, command:str, retry:bool=True) -> Optional[str]:
        _log.debug('sendCommand(%s,%s,%s)',port,command,retry)
        res:Optional[str] = None
        if not self.SP.is_open:
            self.openPort(port)
        try:
            if self.SP.is_open:
                self.SP.reset_input_buffer() # needed to avoid to interpret leftovers from the buffer
                self.SP.reset_output_buffer()
                self.SP.write(str2cmd('\n' + command + '\n'))
                self.SP.flush()
                time.sleep(0.3)
                r:bytes = self.SP.readline()
                response:str = cmd2str(r)
                _log.debug('response(%s): %s',len(response),response.strip())
                if not (response and len(response) > 0):
                    # we got an empty line, maybe the next line contains the response
                    r = self.SP.readline()
                    response = cmd2str(r)
                    _log.debug('second response(%s):%s',len(response),response.strip())
                if response and len(response) > 0:
                    # each <command> is answered by the Tonino by returning "<command>:<result>\n"
                    parts:list[str] = response.split(command + self.cmdSeparatorChar)
                    if parts and len(parts) == 2:
                        res = parts[1].strip()
                    elif parts and len(parts) == 1:
                        res = ''
            if retry and res == None:
                return self.sendCommand(port,command,False)
            else:
                _log.debug('result: %s',res)
                return res
        except Exception as e:  # pylint: disable=broad-except
            _log.exception(e)
            self.closePort()
            if retry:
                return self.sendCommand(port,command,False)
            else:
                return None

    def getSerialPorts(self) -> list[serial.tools.list_ports_common.ListPortInfo]:
        # we are looking for
        #   Classic Tonino: VID 403(hex)/1027(dec) and PID 6001(hex)/24577(dec)
        #      Tiny Tonino: VID 403(hex)/1027(dec) and PID 6015(hex)/24597(dec)
        vid:int = 1027 # 403 (hex)
        # ClassicTonino model (0)
#        classicToninoProduct:str = "VID_0403\+PID_6001"
        classicToninoPID:int = 24577 # 6001 (hex)
        # TinyTonino model (1)
#        tinyToninoProduct:str = "VID_0403\+PID_6015"
        tinyToninoPID:int = 24597 # 6015 (hex)
        ports:list[serial.tools.list_ports_common.ListPortInfo]
        tinyToninos:list[serial.tools.list_ports_common.ListPortInfo]
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

    def filter_ports_by_vid_pid(self,ports:list[serial.tools.list_ports_common.ListPortInfo],vid:Optional[int]=None,pid:Optional[int]=None) -> Iterator[serial.tools.list_ports_common.ListPortInfo]:
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
                        yield port
            except Exception as e:  # pylint: disable=broad-except
                _log.exception(e)

#    def sendReset(self, port:str) -> None:
#        if not self.SP.is_open:
#            self.openPort(port)
#        try:
#            if self.SP.is_open:
#                self.SP.dtr = False
#                time.sleep(0.1)
#                self.SP.dtr = True
#                self.closePort()
#        except:
#            self.closePort()
