#!/usr/bin/python3
#
# setup-mac3.py
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

#from distutils import sysconfig
#their_parse_makefile = sysconfig.parse_makefile
#def my_parse_makefile(filename, g):
#    their_parse_makefile(filename, g)
#    g['MACOSX_DEPLOYMENT_TARGET'] = '10.13'
#sysconfig.parse_makefile = my_parse_makefile

import os
import subprocess
from setuptools import setup

import plistlib

from PyQt6.QtCore import QDir

import lib
import sys

# current version
VERSION = lib.__version__
LICENSE = 'GNU General Public License (GPL)'


try:
    QTDIR = os.environ['QT_PATH'] + r'/'
except Exception:
    from os.path import expanduser
    HOME = expanduser('~')
    QTDIR = HOME + r'/Qt5.14.2/5.14.2/clang_64/'

APP = ['tonino.py']



DATA_FILES:list[tuple[str, list[str]]] = [
    ('.', ['doc/LICENSE.txt']),
#    ("../Resources/qt_plugins/iconengines", [QTDIR + r'/plugins/iconengines/libqsvgicon.dylib']),
#    ("../Resources/qt_plugins/imageformats", [QTDIR + r'/plugins/imageformats/libqsvg.dylib']),
## Qt5 only:
#    ("../Resources/qt_plugins/platforms", [QTDIR + r'/plugins/platforms/libqcocoa.dylib']),
## standard QT translation needed to get the Application menu bar and
## the standard dialog elements translated
#    ("../Resources/qt_plugins/printsupport", [QTDIR + r'/plugins/printsupport/libcocoaprintersupport.dylib']), # qt5/
#    ("../Resources/qt_plugins/styles", [QTDIR + r'/plugins/styles/libqmacstyle.dylib']), # QT 5.10 and later requires this (not available on 5.8)
# standard
    ('../Resources/translations', [QTDIR + r'/translations/qtbase_de.qm']),
    ('../Resources/translations', [QTDIR + r'/translations/qtbase_es.qm']),
    ('../Resources/translations', [QTDIR + r'/translations/qtbase_fr.qm']),
    ('../Resources/translations', [QTDIR + r'/translations/qtbase_it.qm']),
    ('../Resources/translations', [r'translations/tonino_de.qm']),
    ('../Resources/translations', [r'translations/tonino_es.qm']),
    ('../Resources/translations', [r'translations/tonino_fr.qm']),
    ('../Resources/translations', [r'translations/tonino_it.qm']),
    ('../Resources/translations', [r'translations/tonino_nl.qm']),
    ('../Resources/translations', [r'translations/qtbase_nl.qm']),
#    ("../Resources", [r"conf/qt.conf"]),
    ('../Resources', [r'includes/mac/avrdude.conf']),
    ('../Resources', [r'includes/mac/avrdude']),
    ('../Resources', [r'includes/logging.yaml']),
    ('../Resources', [r'icons/tonino_doc.icns']),
  ]

# firmware file name
qd_include = QDir(os.path.dirname(os.path.realpath(__file__)) + '/includes/')
firmware_files = qd_include.entryInfoList(['tonino-*.hex'],QDir.Filter.Files | QDir.Filter.Readable,QDir.SortFlag.Name | QDir.SortFlag.Reversed)
tiny_firmware_files = qd_include.entryInfoList(['tinyTonino-*.hex'],QDir.Filter.Files | QDir.Filter.Readable,QDir.SortFlag.Name | QDir.SortFlag.Reversed)
if len(firmware_files) + len(tiny_firmware_files) > 0:
    if len(firmware_files) > 0:
        firmware_name = str(firmware_files[0].fileName())
        DATA_FILES = DATA_FILES + [('../Resources', [r'includes/' + firmware_name])]
    if len(tiny_firmware_files) > 0:
        tiny_firmware_name = str(tiny_firmware_files[0].fileName())
        DATA_FILES = DATA_FILES + [('../Resources', [r'includes/' + tiny_firmware_name])]
else:
    print('firmware *.hex missing!')
    sys.exit()

with open('conf/Info.plist', 'r+b') as fp:
    plist:dict[str,str | bool | tuple[str]] = plistlib.load(fp)
    plist['CFBundleDisplayName'] = 'Tonino'
    plist['CFBundleGetInfoString'] = 'Tonino, Roast Color Analyzer'
    plist['CFBundleIdentifier'] = 'com.tonino'
    plist['CFBundleShortVersionString'] = VERSION
    plist['CFBundleVersion'] = 'Tonino ' + VERSION
    plist['LSMinimumSystemVersion'] = os.environ['MACOSX_DEPLOYMENT_TARGET']
    plist['LSMultipleInstancesProhibited'] = 'false'
#    plist['LSPrefersPPC'] = False, # not used any longer
    plist['LSArchitecturePriority'] = 'x86_64'
    plist['NSHumanReadableCopyright'] = LICENSE
    plist['NSHighResolutionCapable'] = True
    fp.seek(0, os.SEEK_SET)
    fp.truncate()
    plistlib.dump(plist, fp)

OPTIONS = {
    'strip':False,
    'argv_emulation': False,
    'semi_standalone': False,
    'site_packages': True,
    'packages': ['numpy','scipy','matplotlib', 'PIL'],
    'optimize':  2,
    'compressed': True,
    'iconfile': 'icons/tonino.icns',
    'arch': 'x86_64',
    'matplotlib_backends': '-', # '-' for imported or explicit 'qt4agg' (without this, the full matplotlib folder is again included in Resources/lib (see above)
    'includes': ['serial',
                 'pydoc'],
    'excludes' :  ['tkinter','curses',
                      'PyQt5', # standard builds are now running on PyQt6. If PyQt5 is not excluded here it will be included in Resources/lib/python310.zip
                ],
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

# add localization stubs to make OS X translate the systems menu item and native dialogs
for lang in ['de','en','es','fr','it','nl']:
    loc_dir = r'Tonino.app/Contents/Resources/' + lang + r'.lproj'
    subprocess.check_call(r'mkdir ' + loc_dir,shell = True)
    subprocess.check_call(r'touch ' + loc_dir + r'/Localizable.string',shell = True)


# for Qt
print('*** Removing unused Qt frameworks ***')

# QT modules to keep frameworks:
Qt_modules = [
    'QtCore',
    'QtGui',
    'QtWidgets',
    'QtSvg',
    'QtPrintSupport',
    'QtDBus',
]
Qt_frameworks = [module + '.framework' for module in Qt_modules]

qt_plugin_dirs = [
    'iconengines',
    'imageformats',
    'platforms',
    'printsupport',
    'styles'
]
qt_plugin_files = [
    'libqsvgicon.dylib',
	'libqsvg.dylib',
    'libqcocoa.dylib',
    'libcocoaprintersupport.dylib',
    'libqmacstyle.dylib'
]


# remove unused Qt frameworks libs (not in Qt_modules_frameworks)
for subdir, dirs, _files in os.walk('./Tonino.app/Contents/Frameworks'):
    for dd in dirs:
        if dd.startswith('Qt') and dir.endswith('.framework') and dd not in Qt_frameworks:
            file_path = os.path.join(subdir, dd)
            print(f'rm -rf {file_path}')
            subprocess.check_call(f'rm -rf {file_path}',shell = True)


# remove duplicate Qt plugins folder
# (py2app v0.26.1 copes non-relocated PlugIns to the toplevel)
try:
    subprocess.check_call('rm -rf ./Tonino.app/Contents/plugins',shell = True)
except Exception:
    pass


for python_version in ['python3.8', 'python3.9', 'python3.10', 'python3.11']:
    rootdir = f'./Tonino.app/Contents/Resources/lib/{python_version}'

    if os.path.isdir(f'{rootdir}/PyQt6'):
        # if PyQt6 exists we remove PyQt5 completely
        try:
            subprocess.check_call(f'rm -rf {rootdir}/PyQt5',shell = True)
        except Exception:
            pass
    # remove Qt artefacts
    for qt_dir in [
            'PyQt5/Qt',
            'PyQt5/bindings',
            'PyQt5/uic',
            'PyQt5/Qt5/translations',
            'PyQt5/Qt5/qml',
            'PyQt5/Qt5/qsci',
#            "PyQt5/Qt5/lib", # comment for the non-Framework variant
            'PyQt6/Qt',
            'PyQt6/bindings',
            'PyQt6/lupdate',
            'PyQt6/uic',
            'PyQt6/Qt6/translations',
            'PyQt6/Qt6/qml',
            'PyQt6/Qt6/qsci',
#            "PyQt6/Qt6/lib", # comment for the non-Framework variant
        ]:
        try:
            subprocess.check_call(f'rm -rf {rootdir}/{qt_dir}',shell = True)
        except Exception:
            pass
    for pyqt_dir in ['PyQt5', 'PyQt6']:
        # remove unused PyQt libs (not in Qt_modules)
        for subdir, _dirs, files in os.walk(f'{rootdir}/{pyqt_dir}'):
            for file in files:
                if file.endswith('.pyi'):
                    file_path = os.path.join(subdir, file)
                    subprocess.check_call(f'rm -rf {file_path}',shell = True)
                if file.endswith(('.abi3.so', '.pyi')) and file.split('.')[0] not in Qt_modules:
                    file_path = os.path.join(subdir, file)
                    subprocess.check_call(f'rm -rf {file_path}',shell = True)

# uncomment for non-Framework variant
    # remove unused Qt frameworks libs (not in Qt_modules_frameworks)
    for qt_dir in ['PyQt5/Qt5/lib', 'PyQt6/Qt6/lib']:
        qt = f'{rootdir}/{qt_dir}'
        for _root, dirs, _ in os.walk(qt):
            for dd in dirs:
                if dd.startswith('Qt') and dd.endswith('.framework') and dd not in Qt_frameworks:
                    file_path = os.path.join(qt, dd)
                    subprocess.check_call(f'rm -rf {file_path}',shell = True)

    # remove unused plugins
    for qt_dir in ['PyQt5/Qt5/plugins', 'PyQt6/Qt6/plugins']:
        for root, dirs, _ in os.walk(f'{rootdir}/{qt_dir}'):
            for d in dirs:
                if d not in qt_plugin_dirs:
                    subprocess.check_call('rm -rf ' + os.path.join(root,d),shell = True)
                else:
                    for subdir, _, files in os.walk(os.path.join(root,d)):
                        for file in files:
                            if file not in qt_plugin_files:
                                file_path = os.path.join(subdir, file)
                                subprocess.check_call(f'rm -rf {file_path}',shell = True)
# comment for non-Framework variant
#        # move plugins directory from Resources/lib/python3.x/PyQtX/QtX/plugins to the root of the app
#        try:
#            shutil.move(f"{rootdir}/{qt_dir}", "./Tonino.app/Contents/PlugIns")
#        except Exception:
#            pass


# remove duplicate mpl_data folder
try:
    subprocess.check_call('rm -rf ./Tonino.app/Contents/Resources/mpl-data',shell = True)
except Exception:
    pass
try:
    subprocess.check_call('rm -rf ./Tonino.app/Contents/Resources/lib/python3.10/matplotlib/mpl-data/sample_data',shell = True)
except Exception:
    pass
try:
    subprocess.check_call('rm -rf ./Tonino.app/Contents/Resources/lib/python3.11/matplotlib/mpl-data/sample_data',shell = True)
except Exception:
    pass

print('*** Removing unused files ***')
for root, dirs, files in os.walk('.'):
    for file in files:
        if 'debug' in file:
#            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.startswith('test_'):
#            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.endswith('.pyc') and file != 'site.pyc' and os.path.isfile(os.path.join(root,file[:-3] + 'pyo')):
#            print('Deleting', file)
            os.remove(os.path.join(root,file))
        # remove also all .h .in .cpp .cc .html files
        elif file.endswith('.h') and file != 'pyconfig.h':
#            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.endswith('.in'):
#            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.endswith('.cpp'):
#            print('Deleting', file)
            os.remove(os.path.join(root,file))
        elif file.endswith('.cc'):
#            print('Deleting', file)
            os.remove(os.path.join(root,file))
# .afm files should not be removed as without matplotlib will fail on startup
#        elif file.endswith('.afm'):
#            print('Deleting', file)
#            os.remove(os.path.join(root,file))
    # remove test files
    for dd in dirs:
        if 'tests' in dd:
            for rr,_,ff in os.walk(os.path.join(root, dd)):
                for fl in ff:
#                    print('Deleting', os.path.join(rr,fl))
                    os.remove(os.path.join(rr,fl))

dist_name = r'tonino-mac-' + VERSION + r'.dmg'
os.chdir('..')
os.system(r'rm ' + dist_name)
os.system(r'hdiutil create ' + dist_name + r' -volname "Tonino" -fs HFS+ -srcfolder "dist"')
