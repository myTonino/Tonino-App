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


# PyQt6:
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLibraryInfo, QCoreApplication, QStandardPaths
    
import platform
import os
import sys
import functools
import logging
from typing import Final, Optional

_log: Final = logging.getLogger(__name__)

def main_is_frozen() -> bool:
    ib:bool = False
    try:
        platf:str = str(platform.system())
        if platf == 'Darwin':
            # the sys.frozen is set by py2app and pyinstaller and is unset otherwise
            if getattr( sys, 'frozen', False ):
                ib = True
        elif platf == 'Windows':
            ib = hasattr(sys, 'frozen')
        elif platf == 'Linux':
            if getattr(sys, 'frozen', False):
                # The application is frozen
                ib = True
    except Exception as e: # pylint: disable=broad-except
        _log.exception(e)
    return ib

   
# for py2app and pyinstaller on MacOS X
def inBundle() -> bool:     
    ib:bool = False
    try:
        # the sys.frozen is set by py2app and pyinstaller and is unset otherwise
        if getattr( sys, 'frozen', False ):      
            ib = True
#        if str(sys.frozen) == "macosx_app":
#            ib = True
    except Exception as e: # pylint: disable=broad-except
        _log.exception(e)
    return ib
    
# for bbfreeze or pyinstaller on Linux
def isFrozen() -> bool:
    return sys.executable.endswith("tonino") or getattr(sys, 'frozen', False)
    
            
# returns the path to the platform independent resources
def getResourcePath() -> str:
    res:str = ""
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
def getResourceBinaryPath() -> str:
    res:str = ""
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
def getTranslationsPath() -> str:
    res:str = ""
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
def getSystemTranslationsPath() -> str:
    res:str = ""
    if platform.system() == 'Darwin':
        if inBundle():
            res = QApplication.applicationDirPath() + "/../Resources/translations/"
        else:
            res = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    elif platform.system() == "Linux":
        if isFrozen():
            res = QApplication.applicationDirPath() + "/translations/"
        else:
            res = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    else:
        if main_is_frozen():
            res = os.path.dirname(sys.executable) + "\\translations\\"
        else:
            res = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    return res


# we store data (log files) in the user- and app-specific local default data directory
# for the platform
# note that the path is based on the ApplicationName and OrganizationName
# setting of the app
# eg. ~/Library/Application Support/myTonino/Tonino (macOS)
#     C:/Users/<USER>/AppData/Local/myTonino/Tonino" (Windows)
#     ~/.local/shared/myTonino/Tonino" (Linux)

# getDataDirectory() returns the Tonino data directory
# if app is not yet initialized None is returned
# otherwise the path is computed on first call and then memorized
# if the computed path does not exists it is created
# if creation or access of the path fails None is returned and memorized
def getDataDirectory() -> Optional[str]:
    app:QCoreApplication = QCoreApplication.instance()
    if app is not None:
        return _getAppDataDirectory()
    return None

# internal function to return
@functools.lru_cache(maxsize=None)  #for Python >= 3.9 can use @functools.cache
def _getAppDataDirectory() -> Optional[str]:
    data_dir = QStandardPaths.standardLocations(
        QStandardPaths.StandardLocation.AppLocalDataLocation
    )[0]
    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
    except Exception as e:  # pylint: disable=broad-except
        _log.exception(e)
        return None