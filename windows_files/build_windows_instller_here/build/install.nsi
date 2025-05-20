; AITalk Installer Script
; Created with NSIS (Nullsoft Scriptable Install System)

; Define constants
!define APPNAME "AITalk"
!define COMPANYNAME "AITalk"
!define DESCRIPTION "AITalk Application"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define INSTALLDIR "$PROGRAMFILES32\${APPNAME}"

; Include necessary NSIS components
!include "MUI2.nsh"
!include "LogicLib.nsh"

; Set basic information
Name "${APPNAME}"
OutFile "AITalk_Setup.exe"
InstallDir "${INSTALLDIR}"
InstallDirRegKey HKLM "Software\${APPNAME}" "Install_Dir"
RequestExecutionLevel admin ; Request admin rights for PATH manipulation

; Windows API constants - using different names to avoid conflicts
!define MY_HWND_BROADCAST 0xFFFF
!define MY_WM_WININICHANGE 0x001A

; Include StrReplace function for path manipulation
!macro StrReplace ResultVar String ReplaceFrom ReplaceTo
  Push "${String}"
  Push "${ReplaceFrom}"
  Push "${ReplaceTo}"
  Call StrReplace
  Pop "${ResultVar}"
!macroend
!define StrReplace "!insertmacro StrReplace"

; Include un.StrReplace function for path manipulation in uninstaller
!macro un.StrReplace ResultVar String ReplaceFrom ReplaceTo
  Push "${String}"
  Push "${ReplaceFrom}"
  Push "${ReplaceTo}"
  Call un.StrReplace
  Pop "${ResultVar}"
!macroend
!define un.StrReplace "!insertmacro un.StrReplace"

; Interface settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Set language
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Create the install directory
    CreateDirectory "$INSTDIR"
    
    ; Install the files
    File "aitalk.exe"
    File "aitalk.bat"
    File ".env"
    File "README.txt"
    File "LICENSE.txt"
    
    ; Add directory to PATH (manual implementation)
    ReadRegStr $0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
    StrCpy $1 "$0;$INSTDIR"
    WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" $1
    SendMessage ${MY_HWND_BROADCAST} ${MY_WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
    
    ; Write uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\aitalk.exe"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Write registry keys for uninstallation
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\aitalk.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
SectionEnd

; Uninstaller section
Section "Uninstall"
    ; Remove installed files
    Delete "$INSTDIR\aitalk.exe"
    Delete "$INSTDIR\aitalk.bat"
    Delete "$INSTDIR\.env"
    Delete "$INSTDIR\README.txt"
    Delete "$INSTDIR\LICENSE.txt"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Remove start menu items
    Delete "$SMPROGRAMS\${APPNAME}\*.*"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    ; Remove install directory
    RMDir "$INSTDIR"
    
    ; Remove PATH entry (manual implementation)
    ReadRegStr $0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
    ${un.StrReplace} "$0" ";$INSTDIR" "" $1 ; Remove path if it appears in middle with semicolon
    ${un.StrReplace} "$1" "$INSTDIR;" "" $1 ; Remove path if it appears at beginning with semicolon
    ${un.StrReplace} "$1" "$INSTDIR" "" $1 ; Remove path if it appears alone
    WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" $1
    SendMessage ${MY_HWND_BROADCAST} ${MY_WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
    
    ; Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    DeleteRegKey HKLM "Software\${APPNAME}"
SectionEnd

; String Replace Function for installer
Function StrReplace
  Exch $R2 ; ReplaceTo
  Exch 1
  Exch $R1 ; ReplaceFrom
  Exch 2
  Exch $R0 ; String
  Push $R3
  Push $R4
  Push $R5
  Push $R6
  Push $R7
  
  StrCpy $R3 0
  StrLen $R4 $R1
  StrLen $R6 $R0
  StrLen $R7 $R2
  Loop:
    StrCpy $R5 $R0 $R4 $R3
    StrCmp $R5 $R1 Replace
    StrCmp $R3 $R6 Done
    IntOp $R3 $R3 + 1
    Goto Loop
    
  Replace:
    StrCpy $R5 $R0 $R3
    IntOp $R3 $R3 + $R4
    StrCpy $R6 $R0 "" $R3
    StrCpy $R0 $R5$R2$R6
    IntOp $R3 $R3 - $R4
    IntOp $R3 $R3 + $R7
    IntOp $R6 $R6 + 1
    StrLen $R6 $R0
    Goto Loop
    
  Done:
    Pop $R7
    Pop $R6
    Pop $R5
    Pop $R4
    Pop $R3
    Push $R0
    
    Pop $R0
    Pop $R1
    Pop $R2
    Exch $R0
FunctionEnd

; String Replace Function for uninstaller
Function un.StrReplace
  Exch $R2 ; ReplaceTo
  Exch 1
  Exch $R1 ; ReplaceFrom
  Exch 2
  Exch $R0 ; String
  Push $R3
  Push $R4
  Push $R5
  Push $R6
  Push $R7
  
  StrCpy $R3 0
  StrLen $R4 $R1
  StrLen $R6 $R0
  StrLen $R7 $R2
  Loop:
    StrCpy $R5 $R0 $R4 $R3
    StrCmp $R5 $R1 Replace
    StrCmp $R3 $R6 Done
    IntOp $R3 $R3 + 1
    Goto Loop
    
  Replace:
    StrCpy $R5 $R0 $R3
    IntOp $R3 $R3 + $R4
    StrCpy $R6 $R0 "" $R3
    StrCpy $R0 $R5$R2$R6
    IntOp $R3 $R3 - $R4
    IntOp $R3 $R3 + $R7
    IntOp $R6 $R6 + 1
    StrLen $R6 $R0
    Goto Loop
    
  Done:
    Pop $R7
    Pop $R6
    Pop $R5
    Pop $R4
    Pop $R3
    Push $R0
    
    Pop $R0
    Pop $R1
    Pop $R2
    Exch $R0
FunctionEnd