@ECHO OFF
call .\.venv\Scripts\activate.bat
pyinstaller --noconfirm gui_windows.spec
xcopy .\src\img .\dist\gui\img\ /s /e /h /y
