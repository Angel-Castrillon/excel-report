' ====================================================================
' Lanzador silencioso de Excel Report Dashboard
' Permite hacer doble clic y abrir la aplicación directamente en el
' navegador web SIN dejar una ventana negra de consola visible.
' ====================================================================

Dim WshShell, fso, currentDir
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Obtener la carpeta donde reside este script
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

' Ejecutar python run.py de forma oculta (ventana 0 = invisible, False = no esperar)
WshShell.Run "python run.py", 0, False

Set WshShell = Nothing
Set fso = Nothing
