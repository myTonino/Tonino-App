#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# resources.py
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

try:
    from PyQt5.QtCore import QLibraryInfo
    pyqtversion = 5
except:
    pyqtversion = 4

# PyQt4:
if pyqtversion < 5:    
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QLibraryInfo
# PyQt5:
else:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QLibraryInfo
    
import platform
import os
import sys

# for py2exe on Windows
def main_is_frozen():
    import imp
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze
   
# for py2app and pyinstaller on MacOS X
def inBundle():     
    ib = False
    try:
        # the sys.frozen is set by py2app and pyinstaller and is unset otherwise
        if getattr( sys, 'frozen', False ):      
            ib = True
#        if str(sys.frozen) == "macosx_app":
#            ib = True
    except:
        pass
    return ib
    
# for bbfreeze on Linux
def isFrozen():
    return sys.executable.endswith("tonino")
    
            
# returns the path to the platform independent resources
def getResourcePath():
    res = ""
    if platform.system() == 'Darwin':
        if inBundle():
            res = QApplication.applicationDirPath() + "/../Resources/"
        else:
            res = os.path.dirname(os.path.realpath(__file__)) + "/../includes/"
    elif platform.system() == "Linux":
        if isFrozen():
            res = QApplication.applicationDirPath() + "/includes/"
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
    elif platform.system() == "Linux":
        if isFrozen():
            res = QApplication.applicationDirPath() + "/includes/linux/"
        else:
            res = os.path.dirname(os.path.realpath(__file__)) + "/../includes/linux/"
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
    elif platform.system() == "Linux":
        if isFrozen():
            res = QApplication.applicationDirPath() + "/translations/"
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
    elif platform.system() == "Linux":
        if isFrozen():
            res = QApplication.applicationDirPath() + "/translations/"
        else:
            res = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    else:
        if main_is_frozen():
            res = os.path.dirname(sys.executable) + "\\translations\\"
        else:
            res = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    return res
    
