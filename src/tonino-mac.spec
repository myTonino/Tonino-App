# -*- mode: python ; coding: utf-8 -*-

import os
import subprocess
import plistlib

import sys
sys.path.insert(1, SPECPATH)
import lib  # previous line needed to successfully load local module lib

onefile = False
block_cipher = None

# current version
VERSION = lib.__version__
LICENSE = 'GNU General Public License (GPL)'

try:
    QTDIR = os.environ['QT_PATH'] + r'/'
except Exception:
    from os.path import expanduser
    HOME = expanduser('~')
    QTDIR = HOME + r'/Qt/6.10.0/macos/'


DATA_FILES:list[tuple[str, str]] = [
    (r'Assets.car', '.'),
    ('doc/LICENSE.txt', '.'),
    (QTDIR + r'/translations/qtbase_de.qm', './translations'),
    (QTDIR + r'/translations/qtbase_es.qm', './translations'),
    (QTDIR + r'/translations/qtbase_fr.qm', './translations'),
    (QTDIR + r'/translations/qtbase_it.qm', './translations'),
    (r'translations/tonino_de.qm', './translations'),
    (r'translations/tonino_es.qm', './translations'),
    (r'translations/tonino_fr.qm', './translations'),
    (r'translations/tonino_it.qm', './translations'),
    (r'translations/tonino_nl.qm', './translations'),
    (r'translations/qtbase_nl.qm', './translations'),
    (r'includes/mac/avrdude.conf', '.'),
    (r'includes/mac/avrdude', '.'),
    (r'includes/logging.yaml', '.'),
    (r'includes/tinyTonino-2.2.0.hex', '.'),
    (r'includes/tonino-1.1.7.hex', '.'),
    (r'icons/tonino_doc.icns', '.')
  ]

a = Analysis(['tonino.py'],
             binaries=[],
             datas=DATA_FILES,
             hiddenimports=[],
             hooksconfig={
                'matplotlib': {
                'backends': ['QtAgg']
                },
             },
             hookspath=[],
             runtime_hooks=['./pyinstaller_hooks/rthooks/pyi_rth_mplconfig.py'], # overwrites default MPL runtime hook which keeps loading font cache from (new) temp directory
             additional_hooks_dir=[],
             excludes= ['mypy'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
            a.scripts,
            a.binaries if onefile else [],
            a.zipfiles if onefile else [],
            a.datas if onefile else [],
            exclude_binaries=not onefile,
            name='Tonino',
            debug=False,
            bootloader_ignore_signals=False,
            strip=True,
            upx=False,  # binary compressor: https://github.com/upx/upx
            upx_exclude=[],
            runtime_tmpdir=None,
            console=False,
            disable_windowed_traceback=False,
            argv_emulation=False, # False for GUI apps
            target_arch='universal2', #'x86_64', #'arm64',
            codesign_identity='6M3Z6W45L4', #None,
            entitlements_file='Tonino.entitlements' #None
            )


plist = {}
with open('conf/Info.plist', 'rb') as infile:
    plist = plistlib.load(infile)
plist.update({ 'CFBundleDisplayName': 'Tonino',
                    'CFBundleGetInfoString': 'Tonino, Roast Color Analyzer',
                    'CFBundleIdentifier': 'com.tonino',
                    'CFBundleShortVersionString': VERSION,
                    'CFBundleVersion': 'Tonino ' + VERSION,
                    'LSMinimumSystemVersion': '12.0',
                    'LSMultipleInstancesProhibited': False,
                    'LSArchitecturePriority': ['arm64', 'x86_64'],
                    'NSHumanReadableCopyright': LICENSE,
                    'NSHighResolutionCapable': True,
#                    'UIDesignRequiresCompatibility': True, # run in compatibility mode, keeping the existing look and metrics of pre v26 macOS releases
                    'CFBundleIconName': 'tonino-liquid-glass'
                })

bundle_obj = exe

if not onefile:
    coll = COLLECT(
            exe,
            a.binaries,
            a.zipfiles,
            a.datas,
            strip=True, # not recommended for Windows
            upx=False,  # brew install upx # UPX is currently used only on Windows
            upx_exclude=[],
            name='Test',
        )
    bundle_obj = coll

app = BUNDLE(bundle_obj,
          name='Tonino.app',
          icon='icons/tonino.icns',
          bundle_identifier='com.tonino',
          info_plist=plist)

#------

os.system(r'rm -rf dist/Test')
os.system(r'cp doc/README.txt dist')
os.system(r'cp doc/LICENSE.txt dist')
os.system(r'mkdir dist/scales')
os.system(r'cp scales/*.toni dist/scales')
os.chdir('./dist')

# add localization stubs to make macOS translate the systems menu item and native dialogs
for lang in ['de','en','es','fr','it','nl']:
    loc_dir = r'Tonino.app/Contents/Resources/' + lang + r'.lproj'
    subprocess.check_call(r'mkdir ' + loc_dir,shell = True)
    subprocess.check_call(r'touch ' + loc_dir + r'/Localizable.string',shell = True)


dist_name = r'tonino-mac-' + VERSION + r'.dmg'
os.chdir('..')
os.system(r'rm ' + dist_name)
os.system(r'hdiutil create ' + dist_name + r' -volname "Tonino" -fs HFS+ -srcfolder "dist"')
