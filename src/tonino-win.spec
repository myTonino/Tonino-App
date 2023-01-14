# -*- mode: python -*-

block_cipher = None


TONINO_SRC = r'C:\Users\luther\Desktop\tonino-src'
PYTHON3 = r'C:\Program Files\Python311'
NAME = 'tonino'

##
TARGET = 'dist\\' + NAME + '\\'
PYTHON_PACKAGES = PYTHON3 + r'\Lib\site-packages'
PYQT_QT = PYTHON_PACKAGES + r'\PyQt6\Qt'
PYQT_QT_BIN = PYQT_QT + r'\bin'
PYQT_QT_TRANSLATIONS = PYQT_QT + r'\translations'

a = Analysis(['tonino.py'],
             pathex=[PYQT_QT_BIN, TONINO_SRC],
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
          exclude_binaries=True,
          name=NAME,
          debug=False,
          strip=False, # =True fails
          upx=True, # not installed
          icon=r'icons\tonino.ico',
          console=False )


coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False, # =True fails
               upx=True, # not installed
               name=NAME)



# assumes the Microsoft Visual C++ 2015 Redistributable Package (x64), vc_redist.x64.exe, is located above the source directory
os.system(r'copy ..\vc_redist.x64.exe ' + TARGET)

os.system(r'copy doc\README.txt ' + TARGET)
os.system(r'copy doc\LICENSE.txt ' + TARGET)

os.system('mkdir ' + TARGET + 'translations')
os.system(r'copy translations\*.qm ' + TARGET + 'translations')
for tr in [
    'qtbase_de.qm',
    'qtbase_es.qm',
    'qtbase_fr.qm',
    'qtbase_it.qm',
    ]:
  os.system(r'copy "' + PYQT_QT_TRANSLATIONS + '\\' + tr + '" ' + TARGET + 'translations')

os.system('rmdir /q /s ' + TARGET + 'mpl-data\\sample_data')

for fn in [
    r'icons\tonino.png',
    r'icons\tonino.ico',
    r'icons\tonino_doc.ico',
    r'includes\windows\avrdude.conf',
    r'includes\windows\avrdude.exe',
    r'includes\windows\libusb0.dll',
    r'includes\windows\libusb0.sys',
    r'includes\windows\libusb0_x64.dll',
    r'includes\windows\libusb0_x64.sys',
    r'includes\logging.yaml',
    r'includes\*.hex',
]:
  os.system('copy ' + fn + ' ' + TARGET)


os.system('mkdir dist\\scales')
os.system('copy scales\\*.toni dist\\scales')
