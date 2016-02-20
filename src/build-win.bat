rem
rem build-win.bat
rem
rem Copyright (c) 2016, Paul Holleis, Marko Luther
rem All rights reserved.
rem 
rem 
rem LICENSE
rem
rem This program is free software: you can redistribute it and/or modify
rem it under the terms of the GNU General Public License as published by
rem the Free Software Foundation, either version 3 of the License, or
rem (at your option) any later version.
rem
rem This program is distributed in the hope that it will be useful,
rem but WITHOUT ANY WARRANTY; without even the implied warranty of
rem MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
rem GNU General Public License for more details.
rem
rem You should have received a copy of the GNU General Public License
rem along with this program.  If not, see <http://www.gnu.org/licenses/>.

@echo off

setlocal enableextensions enabledelayedexpansion

set PATH=%PATH%;C:\Python27\Lib\site-packages\PyQt4\
set QMAKE=E:\Qt\bin\qmake.exe
 
rem # ui
for %%I in (ui\*.ui) do call pyuic4.bat -o uic\%%~nI.py --from-imports ui\%%~nI.ui

rem # qrc
for %%I in (qrc\*.qrc) do call pyrcc4 -o "uic\%%~nI_rc.py" "qrc\%%~nI".qrc

rem # translations
pylupdate4 conf\tonino.pro
lrelease -verbose conf\tonino.pro

rem # distribution
C:\Python27\python setup-win.py py2exe

rem #
rem # Don't make assumptions as to where the 'makensis.exe' is - look in the obvious places
rem #
if exist "C:\Program Files (x86)\NSIS\makensis.exe" set NSIS_EXE="C:\Program Files (x86)\NSIS\makensis.exe"
if exist "C:\Program Files\NSIS\makensis.exe"       set NSIS_EXE="C:\Program Files\NSIS\makensis.exe"
if exist "%ProgramFiles%\NSIS\makensis.exe"         set NSIS_EXE="%ProgramFiles%\NSIS\makensis.exe"
if exist "%ProgramFiles(x86)%\NSIS\makensis.exe"    set NSIS_EXE="%ProgramFiles(x86)%\NSIS\makensis.exe"

rem #
rem # Backup - use the one found in the path
rem #
set NSIS_EXE
if %ERRORLEVEL% NEQ 0 set NSIS_EXE="makensis.exe"

rem #
rem #
rem #
%NSIS_EXE% setup-install.nsi
