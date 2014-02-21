#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# setup-mac3.py
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

from distutils import sysconfig
their_parse_makefile = sysconfig.parse_makefile
def my_parse_makefile(filename, g):
    their_parse_makefile(filename, g)
    g['MACOSX_DEPLOYMENT_TARGET'] = '10.6'
sysconfig.parse_makefile = my_parse_makefile

import sys, os
from setuptools import setup

import string
from plistlib import Plist

from PyQt4.QtCore import (QDir)


import lib

# current version
VERSION = lib.__version__
LICENSE = 'GNU General Public License (GPL)'


#Qt4:
QTDIR = r'/Developer/Applications/Qt/'
# Qt5:
#from os.path import expanduser
#HOME = expanduser("~")
#QTDIR = HOME + r'/Qt5.1.1/5.1.1/clang_64/'

APP = ['tonino.py']

# firmware file name
qd_include = QDir(os.path.dirname(os.path.realpath(__file__)) + "/includes/")
firmware_files = qd_include.entryInfoList(["tonino-*.hex"],QDir.Files | QDir.Readable,QDir.SortFlags(QDir.Name | QDir.Reversed))
if len(firmware_files) > 0:
    firmware_name = firmware_files[0].fileName()
else:
    print("firmware *.hex missing!")
    quit()

DATA_FILES = [
    "doc/LICENSE.txt",
    ("../Resources/qt_plugins/iconengines", [QTDIR + r'/plugins/iconengines/libqsvgicon.dylib']),
    ("../Resources/qt_plugins/imageformats", [QTDIR + r'/plugins/imageformats/libqsvg.dylib']),
# Qt5 only:
#    ("../Resources/qt_plugins/platforms", [QTDIR + r'/plugins/platforms/libqcocoa.dylib']),
# standard QT translation needed to get the Application menu bar and 
# the standard dialog elements translated
    ("../Resources/translations", [QTDIR + r'/translations/qt_de.qm']),
    ("../Resources/translations", [QTDIR + r'/translations/qt_es.qm']),
    ("../Resources/translations", [QTDIR + r'/translations/qt_fr.qm']),
    ("../Resources/translations", [r"translations/tonino_de.qm"]),
    ("../Resources/translations", [r"translations/tonino_es.qm"]),
    ("../Resources/translations", [r"translations/tonino_fr.qm"]),
    ("../Resources/translations", [r"translations/tonino_it.qm"]),
    ("../Resources/translations", [r"translations/tonino_nl.qm"]),
    ("../Resources", [r"conf/qt.conf"]),
    ("../Resources", [r"includes/mac/avrdude.conf"]),
    ("../Resources", [r"includes/mac/avrdude"]),
    ("../Resources", [r"includes/" + firmware_name]),
    ("../Resources", [r"icons/tonino_doc.icns"]),
  ]
  
plist = Plist.fromFile('conf/Info3.plist')
plist.update({ 'CFBundleDisplayName': 'Tonino',
                    'CFBundleGetInfoString': 'Tonino, Roast Color Analyzer',
                    'CFBundleIdentifier': 'com.tonino',
                    'CFBundleShortVersionString': VERSION,
                    'CFBundleVersion': 'Tonino ' + VERSION,
                    'LSMinimumSystemVersion': '10.6',
                    'LSMultipleInstancesProhibited': 'false',
                    'LSPrefersPPC': False,
                    'LSArchitecturePriority': 'x86_64',
                    'NSHumanReadableCopyright': LICENSE,
                })
  
OPTIONS = {
    'strip':True,
    'argv_emulation': True,
    'semi_standalone': False,
    'site_packages': True,
#    'packages': ['matplotlib'], # adds full package to Resources/lib/python3.3/matplotlib
    'optimize':  2,
    'compressed': True,
    'iconfile': 'icons/tonino.icns',
    'arch': 'x86_64',
    'matplotlib_backends': '-', # '-' for imported or explicit 'qt4agg' (without this, the full matplotlib folder is again included in Resources/lib (see above)
    'includes': ['serial',
# PyQt5
#                 'PyQt5',
#                 'PyQt5.QtCore',
#                 'PyQt5.QtGui',
#                 'PyQt5.QtWidgets',
#                 'PyQt5.QtSvg'],
# PyQt4
                 'PyQt4.QtCore',
                 'PyQt4.QtGui',
                 'PyQt4.QtSvg'],
    'excludes' :  ['_tkagg','_ps','_fltkagg','Tkinter','Tkconstants',
                      '_agg','_cairo','_gtk','gtkcairo','pydoc','sqlite3',
                      'bsddb','curses','tcl',
                      '_wxagg','_gtagg','_cocoaagg','_wx'],
    'plist'    : plist}

setup(
    name='Tonino',
    version=VERSION,
    author='Marko Luther',
    author_email='marko.luther@gmx.net',
    license=LICENSE,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)

            
os.system(r'cp doc/README.txt dist')
os.system(r'cp doc/LICENSE.txt dist')
os.system(r'mkdir dist/scales')
os.system(r'cp scales/*.toni dist/scales')
os.chdir('./dist')

print('*** Removing Qt debug libs ***')
for root, dirs, files in os.walk('.'):
    for file in files:
        if 'debug' in file:
            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.startswith('test_'):
            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif '_tests' in file:
            print('Deleting', file)            
            os.remove(os.path.join(root,file))            
        elif file.endswith('.pyc') and file != "site.pyc":
            print('Deleting', file)
            os.remove(os.path.join(root,file))
        # remove also all .h .in .cpp .cc .html files 
        elif file.endswith('.h') and file != "pyconfig.h":
            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.endswith('.in'):
            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.endswith('.cpp'):
            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.endswith('.cc'):
            print('Deleting', file)
            os.remove(os.path.join(root,file))
    # remove test files        
    for dir in dirs:
        if 'tests' in dir:
            for r,d,f in os.walk(os.path.join(root,dir)):
                for fl in f:
                    print('Deleting', os.path.join(r,fl))
                    os.remove(os.path.join(r,fl))                

dist_name = r"tonino-mac-" + VERSION + r".dmg"
os.chdir('..')
os.system(r"rm " + dist_name)
os.system(r'hdiutil create ' + dist_name + r' -volname "Tonino" -fs HFS+ -srcfolder "dist"')

