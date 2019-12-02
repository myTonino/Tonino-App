#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tonino.py
#
# Copyright (c) 2016, Paul Holleis, Marko Luther
# All rights reserved.
# 
#
# ABOUT
#
# This program allows to configure the Tonino roast color analyzer
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

"""
Start the application.
"""

import sys
import os

from platform import system

# needs to be done before any other PyQt import
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

# on Qt5, the platform plugin cocoa is not found in the plugin directory (dispite the qt.conf file) if we do not
# extend the libraryPath accordingly
if system() == 'Darwin':
    try:
        if str(sys.frozen) == "macosx_app":
            from PyQt5.QtWidgets import QApplication
            QApplication.addLibraryPath(str(os.path.dirname(os.path.abspath( __file__ ))) + "/qt_plugins/")
    except:
        try:
            if str(sys.frozen) == "macosx_app":
                from PyQt4.QtGui import QApplication
                QApplication.addLibraryPath(str(os.path.dirname(os.path.abspath( __file__ ))) + "/qt_plugins/")
        except:
            pass
elif system().startswith("Windows"):
    try:
        ib = (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze
        from PyQt5.QtWidgets import QApplication
        if ib:
            QApplication.addLibraryPath(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "plugins"))            
        else:
            import site
            QApplication.addLibraryPath(os.path.dirname(site.getsitepackages()[0]) + "\\PyQt5\\plugins")
    except Exception:
        try:
            from PyQt4.QtGui import QApplication
            if ib:
                QApplication.addLibraryPath(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "plugins"))
            else:
                import site
                QApplication.addLibraryPath(os.path.dirname(site.getsitepackages()[0]) + "\\PyQt4\\plugins")
        except:
            pass
else: # Linux
    try:
        ib = getattr(sys, 'frozen', False)
        from PyQt5.QtWidgets import QApplication
        if ib: # on linux delete the matplotlib cache path set to /tmp by pyinstaller
            try:
                os.environ.pop("MPLCONFIGDIR")
            except:
                pass
        if ib:
            QApplication.addLibraryPath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources/qt_plugins"))            
        else:
            import site
            QApplication.addLibraryPath(os.path.dirname(site.getsitepackages()[0]) + "/PyQt5/qt_plugins")
    except Exception:
        try:
            from PyQt4.QtGui import QApplication
            if ib:
                QApplication.addLibraryPath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Resources/qt_plugins"))
            else:
                import site
                QApplication.addLibraryPath(os.path.dirname(site.getsitepackages()[0]) + "/PyQt4/qt_plugins")
        except:
            pass
        
# supress any console/error-log output on all platforms, but Mac OS X
#if not sys.platform.startswith("darwin"):   
#   sys.stderr = sys.stdout = os.devnull
    
import numpy
from lib import main

if __name__ == '__main__':
    with numpy.errstate(invalid='ignore'):
        main.app.exec_()


# EOF
