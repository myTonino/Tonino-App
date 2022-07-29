#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setup-win.py
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

from distutils.core import setup
import matplotlib as mpl
import py2exe

import os

# Remove the build folder, a bit slower but ensures that build contains the latest
import shutil
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)


INCLUDES = [
            "sip",
            "serial",
            "scipy.special._ufuncs_cxx",
            "scipy.sparse.csgraph._validation",
            "scipy.integrate",
            "scipy.interpolate",
            "scipy.linalg.cython_blas",
            "scipy.linalg.cython_lapack",
#            "urlparse",
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
            '_wx',
            ]

# current version of Tonino

import lib
VERSION = lib.__version__
LICENSE = 'GNU General Public License (GPL)'

cwd = os.getcwd()

DATAFILES = mpl.get_py2exe_datafiles()
DATAFILES = DATAFILES + \
    [('plugins\\imageformats', [
            'c:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\imageformats\\qsvg.dll',
            ]),
      ('plugins\\iconengines', [
            'c:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\iconengines\\qsvgicon.dll',
            ]),
      ('plugins\\platforms', [
            'c:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\platforms\\qwindows.dll',
            ]),
      ('plugins\\printsupport', [
            'c:\\Python34\\Lib\\site-packages\\PyQt5\\plugins\\printsupport\\windowsprintersupport.dll',
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
#                        'optimize':  2, # breaks py2exe on py3
#                        "bundle_files": 2, # default bundle_files: 3 breaks WebLCDs on Windows
      # bundle_files 1 or 2 breaks py2exe on py3 in gevent._semahores
                        "dll_excludes":[
                            'MSVCP90.dll','tcl84.dll','tk84.dll','libgdk-win32-2.0-0.dll',
                            'libgdk_pixbuf-2.0-0.dll','libgobject-2.0-0.dll',
                            'MSVCR90.dll','MSVCN90.dll','mwsock.dll','powrprof.dll'],
                        "includes" : INCLUDES,
                        "excludes" : EXCLUDES
                        }
            }
    )

os.system('mkdir dist')
os.system('mkdir build')
os.system('copy doc\\README.txt dist')
os.system('copy doc\\LICENSE.txt dist')
os.system('copy conf\\qt-win.conf dist\\qt.conf')
os.system('mkdir dist\\translations')
os.system('copy translations\\*.qm dist\\translations')
os.system('copy c:\\Python34\\Lib\\site-packages\\PyQt5\\translations\\qt_de.qm dist\\translations')
os.system('copy c:\\Python34\\Lib\\site-packages\\PyQt5\\translations\\qt_it.qm dist\\translations')
os.system('copy c:\\Python34\\Lib\\site-packages\\PyQt5\\translations\\qt_es.qm dist\\translations')
os.system('copy c:\\Python34\\Lib\\site-packages\\PyQt5\\translations\\qt_fr.qm dist\\translations')
os.system('rmdir /q /s dist\\mpl-data\\sample_data')
os.system('copy icons\\tonino.png dist')
os.system('copy icons\\tonino_doc.ico dist')
os.system('copy ..\\Redistribution2010\\vcredist_x86.exe dist')
#os.system('copy ..\\CDM20830_Setup.exe dist')
os.system('copy includes\\windows\\avrdude.conf dist')
os.system('copy includes\\windows\\avrdude.exe dist')
os.system('copy includes\\windows\\libusb0.dll dist')
os.system('copy includes\\windows\\libusb0.sys dist')
os.system('copy includes\\windows\\libusb0_x64.dll dist')
os.system('copy includes\\windows\\libusb0_x64.sys dist')
os.system('mkdir dist\\scales')
os.system('copy scales\\*.toni dist\\scales')
os.system('copy includes\\*.hex dist')
