#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# tonino.py
#
# Copyright (c) 2022, Paul Holleis, Marko Luther
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


import warnings
warnings.simplefilter('ignore', DeprecationWarning)

import sys
import os
from platform import system

# on Qt5, the platform plugin cocoa/windows is not found in the plugin directory (dispite the qt.conf file) if we do not
# extend the libraryPath accordingly
if system().startswith('Windows'):
    try:
        ib = (
            hasattr(sys, 'frozen') or # new py2exe
            hasattr(sys, 'importers') # old py2exe
        )
        from PyQt6.QtWidgets import QApplication  # @UnresolvedImport @Reimport @UnusedImport
        if ib:
            QApplication.addLibraryPath(os.path.join(os.path.dirname(os.path.realpath(sys.executable)), 'plugins'))
        else:
            import site # @Reimport @UnusedImport
            QApplication.addLibraryPath(site.getsitepackages()[1] + '\\PyQt6\\plugins')
    except Exception: # pylint: disable=broad-except
        pass
else: # Linux
    try:
        ib = getattr(sys, 'frozen', False)
        from PyQt6.QtWidgets import QApplication  # @UnresolvedImport @Reimport @UnusedImport
        if ib:
            QApplication.addLibraryPath(os.path.join(os.path.dirname(__file__), 'Resources/qt_plugins'))
        else:
            import site # @Reimport
            QApplication.addLibraryPath(os.path.dirname(site.getsitepackages()[0]) + '/PyQt6/qt_plugins')
    except Exception: # pylint: disable=broad-except
        pass
    
import numpy
from lib import main

if __name__ == '__main__':
    with numpy.errstate(invalid='ignore'):
        main.app.exec()


# EOF
