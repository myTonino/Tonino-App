#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# resources.py
#
# Copyright (c) 2013, Paul Holleis, Marko Luther
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

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QLibraryInfo
import platform
import os
import sys

# for py2exe
def main_is_frozen():
    import imp
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze
   
# for py2app
def inBundle():     
    ib = False
    try:
        # the sys.frozen is set by py2app and is unset otherwise
        if str(sys.frozen) == "macosx_app":
            ib = True
    except:
        pass
    return ib
            
# returns the path to the platform independent resources
def getResourcePath():
    res = ""
    if platform.system() == 'Darwin':
        if inBundle():
            res = QApplication.applicationDirPath() + "/../Resources/"
        else:
            res = os.path.dirname(os.path.realpath(__file__)) + "/../includes/"
    else:
        if main_is_frozen():
            res = os.path.dirname(sys.executable) + "\\"
        else:
            res = os.path.dirname(os.path.realpath(__file__)) + "\\..\\includes\\"
    return res

# returns the path to the platform dependent binaries
def getResourceBinaryPath():
    res = ""
    if platform.system() == 'Darwin':
        if inBundle():
            res = QApplication.applicationDirPath() + "/../Resources/"
        else:
            res = os.path.dirname(os.path.realpath(__file__)) + "/../includes/mac/"
    else:
        if main_is_frozen():
            res = os.path.dirname(sys.executable) + "\\"
        else:
            res = os.path.dirname(os.path.realpath(__file__)) + "\\..\\includes\\windows\\"
    return res
    
# returns the path to the translations
def getTranslationsPath():
    res = ""
    if platform.system() == 'Darwin':
        if inBundle():
            res = QApplication.applicationDirPath() + "/../Resources/translations/"
        else:
            res = os.path.dirname(os.path.realpath(__file__)) + "/../translations/"
    else:
        if main_is_frozen():
            res = os.path.dirname(sys.executable) + "\\translations\\"
        else:
            res = os.path.dirname(os.path.realpath(__file__)) + "\\..\\translations\\"
    return res
    
    
# returns the path to the qt system translations
def getSystemTranslationsPath():
    res = ""
    if platform.system() == 'Darwin':
        if inBundle():
            res = QApplication.applicationDirPath() + "/../Resources/translations/"
        else:
            res = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    else:
        if main_is_frozen():
            res = os.path.dirname(sys.executable) + "\\translations\\"
        else:
            res = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    return res
    
