@ECHO OFF
call .\.venv\Scripts\activate.bat
pyinstaller --noconfirm gui_windows.spec
xcopy .\src\img .\dist\SeaGapDockerGUI\img\ /s /e /h /y
7z a .\SeaGapDockerGUI_windows.zip .\dist
