; Inno Setup script for PySupervisor (Embedded Python Version)

[Setup]
AppName=PySupervisor
AppVersion=0.9
AppPublisher=B D Dib
ArchitecturesInstallIn64BitMode=x64compatible
DefaultDirName={autopf}\PySupervisor
DefaultGroupName=PySupervisor
AllowNoIcons=yes
OutputDir=.\installer
OutputBaseFilename=PySupervisor_Embedded_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
; --- FIX: Changed hyphen to colon in {cm:AdditionalIcons} ---
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Dirs]
; Create the user's data directory in AppData\Roaming.
Name: "{userappdata}\PySupervisor"

[Files]
; Copy the entire contents of our prepared source folder to the installation directory.
Source: ".\installer_source\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

; Copy the example config to the user's AppData directory.
Source: ".\config.example.json"; DestDir: "{userappdata}\PySupervisor"; DestName: "config.json"; Flags: onlyifdoesntexist

[Icons]
; The shortcuts now point directly to pythonw.exe and pass main.py as a parameter.
Name: "{group}\PySupervisor"; Filename: "{app}\pythonw.exe"; Parameters: "main.py"; WorkingDir: "{app}"; IconFilename: "{app}\icon.png"
Name: "{autodesktop}\PySupervisor"; Filename: "{app}\pythonw.exe"; Parameters: "main.py"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\icon.png"

[Run]
; Launch the application after installation by calling pythonw.exe directly.
Filename: "{app}\pythonw.exe"; Parameters: "main.py"; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,PySupervisor}"; Flags: nowait postinstall skipifsilent