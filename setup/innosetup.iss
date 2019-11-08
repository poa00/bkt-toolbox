; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "BKT-Toolbox"
#define MyAppPublisher "Business Kasper"
#define MyAppURL "https://www.bkt-toolbox.de"
#define MyAppVersion "2.6.0"
#define MyReleaseDate "191108"
;GetDateTimeString('yymmdd', '', '');

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{BD924AD8-8870-46C1-AAE1-8999D7B18E51}
AppName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
DefaultDirName={localappdata}\BKT-Toolbox
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; NOTE: DisableDirPage auto would not ask for location if previous installation is found
DisableDirPage=no
;DisableReadyPage=yes
OutputDir=_releases
OutputBaseFilename=bkt_install_r{#MyReleaseDate}
Compression=lzma
SolidCompression=yes
SourceDir=..\
PrivilegesRequired=lowest
;SignedUninstaller=yes
WizardStyle=modern
SetupIconFile=setup\bkt_logo.ico
WizardSmallImageFile=setup\bkt_logo_55x55.bmp,setup\bkt_logo_64x68.bmp,setup\bkt_logo_83x80.bmp,setup\bkt_logo_110x106.bmp,setup\bkt_logo_138x140.bmp
UninstallDisplayIcon={uninstallexe}

[Languages]
; Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Types]
Name: "compact"; Description: "Nur PowerPoint-Toolbar"
Name: "full"; Description: "Alle Toolbars und Features"
Name: "custom"; Description: "Benutzerdefinierte Auswahl"; Flags: iscustom

[Components]
Name: "powerpoint"; Description: "PowerPoint"; Types: full
Name: "powerpoint\toolbar"; Description: "PowerPoint Toolbar mit Extras"; Types: full compact custom; Flags: fixed
Name: "powerpoint\consol"; Description: "Tool zum Konsolidieren und Teilen"; Types: full
Name: "powerpoint\customformats"; Description: "Benutzerdefiniere Formatvorlagen"; Types: full
Name: "powerpoint\quickedit"; Description: "QuickEdit Toolbar (Farbleiste)"; Types: full
Name: "powerpoint\statistics"; Description: "Statistiken f�r Shape-Auswahl"; Types: full
Name: "excel"; Description: "Excel"; Types: full
Name: "excel\toolbar"; Description: "Excel Toolbar (BETA)"; Types: full
Name: "excel\calc"; Description: "Sofort-Mini-Rechner"; Types: full
Name: "visio"; Description: "Visio"; Types: full
Name: "visio\toolbar"; Description: "Visio Toolbar (BETA)"; Types: full

[InstallDelete]
Type: filesandordirs; Name: "{app}\resources\cache"
; Type: filesandordirs; Name: "{app}\resources\settings"

[Files]
Source: "bin\*"; DestDir: "{app}\bin"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "bkt\*"; DestDir: "{app}\bkt"; Flags: ignoreversion recursesubdirs
Source: "features\*"; DestDir: "{app}\features"; Flags: ignoreversion recursesubdirs
Source: "installer\*"; DestDir: "{app}\installer"; Flags: ignoreversion recursesubdirs
Source: "modules\*"; DestDir: "{app}\modules"; Flags: ignoreversion recursesubdirs
Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "\cache\*,\settings\*,\registry\local\*,\xml\*"
Source: "documentation\example_feature_folder\*"; DestDir: "{app}\documentation\example_feature_folder"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\AddIn neu registrieren"; Filename: "{app}\installer\install.bat"; WorkingDir: "{app}"
Name: "{group}\Config-Datei �ffnen"; Filename: "{app}\config.txt"
Name: "{group}\BKT-Ordner �ffnen"; Filename: "{app}\"
Name: "{group}\BKT deinstallieren"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m install"; WorkingDir: "{app}\installer"; StatusMsg: "Office-AddIn einrichten..."; Flags: runasoriginaluser; Components: not (excel or visio)
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m install --app excel"; WorkingDir: "{app}\installer"; StatusMsg: "Office-AddIn einrichten..."; Flags: runasoriginaluser; Components: excel and not visio
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m install --app visio"; WorkingDir: "{app}\installer"; StatusMsg: "Office-AddIn einrichten..."; Flags: runasoriginaluser; Components: visio and not excel
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m install --app excel --app visio"; WorkingDir: "{app}\installer"; StatusMsg: "Office-AddIn einrichten..."; Flags: runasoriginaluser; Components: excel and visio

Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m config --add_folder features\ppt_customformats"; WorkingDir: "{app}\installer"; StatusMsg: "PowerPoint Benutzerdef. Formate aktivieren..."; Flags: runasoriginaluser runhidden; Components: powerpoint\customformats
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m config --add_folder features\ppt_consolidation_split"; WorkingDir: "{app}\installer"; StatusMsg: "PowerPoint-Konsolidierungstool aktivieren..."; Flags: runasoriginaluser runhidden; Components: powerpoint\consol
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m config --add_folder features\ppt_quickedit"; WorkingDir: "{app}\installer"; StatusMsg: "PowerPoint-QuickEdit aktivieren..."; Flags: runasoriginaluser runhidden; Components: powerpoint\quickedit
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m config --add_folder features\ppt_statistics"; WorkingDir: "{app}\installer"; StatusMsg: "PowerPoint-Shape-Statistics aktivieren..."; Flags: runasoriginaluser runhidden; Components: powerpoint\statistics
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m config --add_folder features\bkt_excel"; WorkingDir: "{app}\installer"; StatusMsg: "Excel-Toolbar aktivieren..."; Flags: runasoriginaluser runhidden; Components: excel\toolbar
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m config --add_folder features\xls_instacalc"; WorkingDir: "{app}\installer"; StatusMsg: "Excel-Mini-Rechner aktivieren..."; Flags: runasoriginaluser runhidden; Components: excel\calc
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m config --add_folder features\bkt_visio"; WorkingDir: "{app}\installer"; StatusMsg: "Visio-Toolbar aktivieren..."; Flags: runasoriginaluser runhidden; Components: visio\toolbar
; NOTE: use flag "nowait" if problems with hanging script occure
; NOTE: use flag runhidden if DOS window should not show up
  
[UninstallRun]
Filename: "{app}\installer\ipy-2.7.9\ipy.exe"; Parameters: "-m install --uninstall"; WorkingDir: "{app}\installer"

[UninstallDelete]
Type: filesandordirs; Name: "{app}\resources\cache"
Type: filesandordirs; Name: "{app}\resources\xml"