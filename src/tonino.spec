# -*- mode: python -*-

block_cipher = None

a = Analysis(['tonino.py'],
             pathex=['/Users/luther/Documents/Projects/Tonino/app/github/Tonino-App/src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes= [],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Tonino',
          debug=False,
          strip=True,
          upx=True,
          console=False )

# prepare Info.plist
import lib
import string
from plistlib import Plist
VERSION = lib.__version__
LICENSE = 'GNU General Public License (GPL)'
plist = Plist.fromFile('conf/Info.plist')
plist.update({ 'CFBundleDisplayName': 'Tonino',
                    'CFBundleGetInfoString': 'Tonino, Roast Color Analyzer',
                    'CFBundleIdentifier': 'com.tonino',
                    'CFBundleShortVersionString': VERSION,
                    'CFBundleVersion': 'Tonino ' + VERSION,
                    'LSMinimumSystemVersion': '10.7',
                    'LSMultipleInstancesProhibited': 'false',
                    'LSPrefersPPC': False,
                    'LSArchitecturePriority': 'x86_64',
                    'NSHumanReadableCopyright': LICENSE,
                })


app = BUNDLE(exe,
          name='Tonino.app',
          icon='icons/tonino.icns',
          bundle_identifier='com.tonino')


import os
os.system(r'rm dist/Tonino.app/Contents/Info.plist')

plist.write(r'dist/Tonino.app/Contents/Info.plist')


