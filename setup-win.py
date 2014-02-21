#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setup-win.py
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

from distutils.core import setup
import matplotlib as mpl
import py2exe

import os

INCLUDES = [
            "sip",
            "serial"
            ]

EXCLUDES = ['_tkagg',
            '_ps',
            '_fltkagg',
            'Tkinter',
            'Tkconstants',
            '_cairo',
            '_gtk',
            'gtkcairo',
            'pydoc',
            'sqlite3',
            'bsddb',
            'curses',
            'tcl',
            '_wxagg',
            '_gtagg',
            '_cocoaagg',
            '_wx']


# current version of Tonino

import lib
VERSION = lib.__version__
LICENSE = 'GNU General Public License (GPL)'

cwd = os.getcwd()

DATAFILES = mpl.get_py2exe_datafiles()
DATAFILES = DATAFILES + \
    [('plugins\imageformats', [
            'c:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll',
            ]),
      ('plugins\iconengines', [
            'c:\Python27\Lib\site-packages\PyQt4\plugins\iconengines\qsvgicon4.dll',
            ]),
    ]

setup(
    name ="Tonino",
    version=VERSION,
    author='Marko Luther',
    author_email='marko.luther@gmx.net',
    license=LICENSE,
    windows=[{"script" : cwd + "\\tonino.py",
            "icon_resources": [(0, cwd + "\\icons\\tonino.ico")]
            }],
    data_files = DATAFILES,
    zipfile = "lib\library.zip",
    options={"py2exe" :{
                        "packages": ['matplotlib','pytz'],
                        "compressed": False, # faster
                        "unbuffered": True,
                        'optimize':  2,
                        "dll_excludes":[
                            'MSVCP90.dll','tcl84.dll','tk84.dll','libgdk-win32-2.0-0.dll',
                            'libgdk_pixbuf-2.0-0.dll','libgobject-2.0-0.dll'],
                        "includes" : INCLUDES,
                        "excludes" : EXCLUDES}
            }
    )

os.system(r'copy doc\\README.txt dist')
os.system(r'copy doc\\LICENSE.txt dist')
os.system(r'copy conf\\qt-win.conf dist\\qt.conf')
os.system(r'mkdir dist\\translations')
os.system(r'copy translations\\*.qm dist\\translations')
os.system(r'copy E:\\Qt\\translations\\qt_de.qm dist\\translations')
os.system(r'copy E:\\Qt\\translations\\qt_es.qm dist\\translations')
os.system(r'copy E:\\Qt\\translations\\qt_fr.qm dist\\translations')
os.system(r'copy icons\\tonino.png dist')
os.system(r'copy icons\\tonino_doc.ico dist')
os.system(r'copy ..\\vcredist_x86.exe dist')
os.system(r'copy ..\\CDM20830_Setup.exe dist')
os.system(r'copy includes\\windows\\avrdude.conf dist')
os.system(r'copy includes\\windows\\avrdude.exe dist')
os.system(r'copy includes\\windows\\libusb0.dll dist')
os.system(r'copy includes\\windows\\libusb0.sys dist')
os.system(r'copy includes\\windows\\libusb0_x64.dll dist')
os.system(r'copy includes\\windows\\libusb0_x64.sys dist')
os.system(r'mkdir dist\\scales')
os.system(r'copy scales\\*.toni dist\\scales')
os.system(r'copy includes\\*.hex dist')
