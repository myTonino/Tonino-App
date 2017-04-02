;
; setup-install.nsi
;
; Copyright (c) 2016, Paul Holleis, Marko Luther
; All rights reserved.
; 
; 
; LICENSE
;
; This program is free software: you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation, either version 3 of the License, or
; (at your option) any later version.
;
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License
; along with this program.  If not, see <http://www.gnu.org/licenses/>.

RequestExecutionLevel admin

!macro APP_ASSOCIATE EXT FILECLASS DESCRIPTION ICON COMMANDTEXT COMMAND
  ; Backup the previously associated file class
  ReadRegStr $R0 HKCR ".${EXT}" ""
  WriteRegStr HKCR ".${EXT}" "${FILECLASS}_backup" "$R0"
 
  WriteRegStr HKCR ".${EXT}" "" "${FILECLASS}"
 
  WriteRegStr HKCR "${FILECLASS}" "" `${DESCRIPTION}`
  WriteRegStr HKCR "${FILECLASS}\DefaultIcon" "" `${ICON}`
  WriteRegStr HKCR "${FILECLASS}\shell" "" "open"
  WriteRegStr HKCR "${FILECLASS}\shell\open" "" `${COMMANDTEXT}`
  WriteRegStr HKCR "${FILECLASS}\shell\open\command" "" `${COMMAND}`
!macroend
 
!macro APP_ASSOCIATE_EX EXT FILECLASS DESCRIPTION ICON VERB DEFAULTVERB SHELLNEW COMMANDTEXT COMMAND
  ; Backup the previously associated file class
  ReadRegStr $R0 HKCR ".${EXT}" ""
  WriteRegStr HKCR ".${EXT}" "${FILECLASS}_backup" "$R0"
 
  WriteRegStr HKCR ".${EXT}" "" "${FILECLASS}"
  StrCmp "${SHELLNEW}" "0" +2
  WriteRegStr HKCR ".${EXT}\ShellNew" "NullFile" ""
 
  WriteRegStr HKCR "${FILECLASS}" "" `${DESCRIPTION}`
  WriteRegStr HKCR "${FILECLASS}\DefaultIcon" "" `${ICON}`
  WriteRegStr HKCR "${FILECLASS}\shell" "" `${DEFAULTVERB}`
  WriteRegStr HKCR "${FILECLASS}\shell\${VERB}" "" `${COMMANDTEXT}`
  WriteRegStr HKCR "${FILECLASS}\shell\${VERB}\command" "" `${COMMAND}`
!macroend
 
!macro APP_ASSOCIATE_ADDVERB FILECLASS VERB COMMANDTEXT COMMAND
  WriteRegStr HKCR "${FILECLASS}\shell\${VERB}" "" `${COMMANDTEXT}`
  WriteRegStr HKCR "${FILECLASS}\shell\${VERB}\command" "" `${COMMAND}`
!macroend
 
!macro APP_ASSOCIATE_REMOVEVERB FILECLASS VERB
  DeleteRegKey HKCR `${FILECLASS}\shell\${VERB}`
!macroend

!macro APP_UNASSOCIATE EXT FILECLASS
  ; Backup the previously associated file class
  ReadRegStr $R0 HKCR ".${EXT}" `${FILECLASS}_backup`
  WriteRegStr HKCR ".${EXT}" "" "$R0"
 
  DeleteRegKey HKCR `${FILECLASS}`
!macroend
 
!macro APP_ASSOCIATE_GETFILECLASS OUTPUT EXT
  ReadRegStr ${OUTPUT} HKCR ".${EXT}" ""
!macroend
 
 
; !defines for use with SHChangeNotify
!ifdef SHCNE_ASSOCCHANGED
!undef SHCNE_ASSOCCHANGED
!endif
!define SHCNE_ASSOCCHANGED 0x08000000
!ifdef SHCNF_FLUSH
!undef SHCNF_FLUSH
!endif
!define SHCNF_FLUSH        0x1000
 
!macro UPDATEFILEASSOC
; Using the system.dll plugin to call the SHChangeNotify Win32 API function so we
; can update the shell.
  System::Call "shell32::SHChangeNotify(i,i,i,i) (${SHCNE_ASSOCCHANGED}, ${SHCNF_FLUSH}, 0, 0)"
!macroend


; HM NIS Edit Wizard helper defines
!define py2exeOutputDir 'dist'
!define PRODUCT_NAME "Tonino"
!define PRODUCT_EXE "tonino.exe"
!define PRODUCT_VERSION "1.0.20.0"
!define PRODUCT_PUBLISHER "Marko Luther, Paul Holleis"
!define PRODUCT_WEB_SITE "http://my-tonino.com"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${PRODUCT_EXE}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

;!define MSVC2008 "http://download.microsoft.com/download/1/1/1/1116b75a-9ec3-481a-a3c8-1777b5381140/vcredist_x86.exe"

Caption "${PRODUCT_NAME} Installer"
VIProductVersion ${PRODUCT_VERSION}
VIAddVersionKey ProductName "${PRODUCT_NAME}"
VIAddVersionKey Comments "Installer for ${PRODUCT_NAME}"
VIAddVersionKey CompanyName "${PRODUCT_PUBLISHER}"
VIAddVersionKey LegalCopyright "${PRODUCT_WEB_SITE}"
VIAddVersionKey FileVersion "${PRODUCT_VERSION}"
VIAddVersionKey FileDescription "${PRODUCT_NAME} ${PRODUCT_VERSION} Installer"
VIAddVersionKey ProductVersion "${PRODUCT_VERSION}"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "icons\tonino.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME}"
OutFile "Setup-${PRODUCT_NAME}-${PRODUCT_VERSION}.exe"
InstallDir "C:\Program Files\${PRODUCT_NAME}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Function .onInit
 
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" \
  "UninstallString"
  StrCmp $R0 "" done  
 
  MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION \
  "${PRODUCT_NAME} is already installed. $\n$\nClick `OK` to remove the \
  previous version or `Cancel` to cancel this upgrade." /SD IDOK \
  IDOK uninst
  Abort
 
;Run the uninstaller
uninst:
  ClearErrors
  IfSilent mysilent nosilent
    
mysilent:
  ExecWait '$R0 /S _?=$INSTDIR' ;Do not copy the uninstaller to a temp file
  IfErrors no_remove_uninstaller done
  
nosilent:
  ExecWait '$R0 _?=$INSTDIR' ;Do not copy the uninstaller to a temp file 
  IfErrors no_remove_uninstaller done
    
no_remove_uninstaller:
    ;You can either use Delete /REBOOTOK in the uninstaller or add some code
    ;here to remove the uninstaller. Use a registry key to check
    ;whether the user has chosen to uninstall. If you are using an uninstaller
    ;components page, make sure all sections are uninstalled.
  
done:
 
FunctionEnd

Section "MainSection" SEC01
  SetShellVarContext all
  SetOutPath "$INSTDIR"
  SetOverwrite on
  File /r '${py2exeOutputDir}\*.*'
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_EXE}"
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_EXE}"
SectionEnd

Section "Microsoft Visual C++ 2008 Redistributable Package (x86)" SEC02
ExecWait '$INSTDIR\vcredist_x86.exe /q:a /c:"VCREDI~3.EXE /q:a /c:""msiexec /i vcredist.msi /qn"" "'
SectionEnd

; Section "FTDI Drivers" SEC03
; ExecWait '$INSTDIR\CDM20830_Setup.exe /q:a /c:"CDM208~3.EXE /q:a /c:""msiexec /i ftdiinstall.msi /qn"" "'
; SectionEnd

Section -AdditionalIcons
  SetShellVarContext all
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\${PRODUCT_EXE}"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "Path" "$INSTDIR"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${PRODUCT_EXE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"

  ; file associations
  !insertmacro APP_ASSOCIATE "toni" "${PRODUCT_NAME}.Document" "${PRODUCT_NAME} Document" \
     "$INSTDIR\tonino_doc.ico" "Open with ${PRODUCT_NAME}" "$INSTDIR\${PRODUCT_EXE} $\"%1$\""
     
SectionEnd


Function un.onUninstSuccess
  HideWindow
  IfSilent +2 0
    MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer." /SD IDOK
FunctionEnd

Function un.onInit

    IfSilent +3 
        MessageBox MB_ICONQUESTION|MB_YESNO|MB_TOPMOST "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2 
        Abort 
    HideWindow   

FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\${PRODUCT_EXE}"
  Delete "$INSTDIR\tonino.png"
  Delete "$INSTDIR\README.txt"
  Delete "$INSTDIR\LICENSE.txt"
  Delete "$INSTDIR\python34.dll"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\tonino_doc.ico"
  Delete "$INSTDIR\qt.conf"
  Delete "$INSTDIR\vcredist_x86.exe"
  Delete "$INSTDIR\avrdude.conf"
  Delete "$INSTDIR\avrdude.exe"
  Delete "$INSTDIR\*.hex"
  Delete "$INSTDIR\libusb0.dll"
  Delete "$INSTDIR\libusb0.sys"
  Delete "$INSTDIR\libusb0_x64.dll"
  Delete "$INSTDIR\libusb0_x64.sys"

  SetShellVarContext all
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\Website.lnk"
  Delete "$DESKTOP\${PRODUCT_NAME}.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"
  
  RMDir /r "$INSTDIR\plugins"
  RMDir /r "$INSTDIR\lib"
  RMDir /r "$INSTDIR\mpl-data"
  RMDir /r "$INSTDIR\translations"
  RMDir /r "$INSTDIR\scales"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"
  RMDir "$INSTDIR"
  
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  DeleteRegKey HKCR ".toni"
  DeleteRegKey HKCR "${PRODUCT_NAME}.Document\DefaultIcon"
  DeleteRegKey HKCR "${PRODUCT_NAME}.Document\shell"
  DeleteRegKey HKCR "${PRODUCT_NAME}.Document\shell\open\command"
  DeleteRegKey HKCR "${PRODUCT_NAME}.Document"
 
  !insertmacro APP_UNASSOCIATE "toni" "${PRODUCT_NAME}.Document"
  
  SetAutoClose true
SectionEnd
