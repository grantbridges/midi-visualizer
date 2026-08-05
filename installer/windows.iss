; installer/windows.iss
;
; Inno Setup script that packages the PyInstaller "onedir" build output
; (dist/Illustri MIDI Studio/) into a proper Windows installer.
;
; The AppVersion is passed in from the GitHub Actions workflow via:
;   ISCC installer\windows.iss /DAppVersion=v1.0.0-beta
; A fallback default is defined below so this also compiles fine locally.

#ifndef AppVersion
  #define AppVersion "0.0.0-dev"
#endif

[Setup]
AppName=Illustri MIDI Studio
AppVersion={#AppVersion}
AppPublisher=Grant Bridges
; The script lives in installer/, but assets/ and dist/ live at the repo
; root - SourceDir tells Inno Setup to resolve relative Source/Icon paths
; below from one directory up (the repo root) instead of from installer/.
SourceDir=..
DefaultDirName={autopf}\Illustri MIDI Studio
DefaultGroupName=Illustri MIDI Studio
DisableProgramGroupPage=yes
; OutputDir is NOT affected by SourceDir - it's always relative to the
; script's own directory - so "..\" is needed here to land at repo root.
OutputDir=..\installer_output
OutputBaseFilename=IllustriMIDIStudio-Setup
SetupIconFile=assets\icons\illustri.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
; No code signing yet - SmartScreen will show an "unrecognized publisher"
; warning until this is signed. Expected for now.

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
; Recursively pulls in the entire onedir build output.
Source: "dist\Illustri MIDI Studio\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Illustri MIDI Studio"; Filename: "{app}\Illustri MIDI Studio.exe"
Name: "{group}\Uninstall Illustri MIDI Studio"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Illustri MIDI Studio"; Filename: "{app}\Illustri MIDI Studio.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Illustri MIDI Studio.exe"; Description: "Launch Illustri MIDI Studio"; Flags: nowait postinstall skipifsilent
