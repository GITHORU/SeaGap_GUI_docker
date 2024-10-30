#!/bin/bash 
source venv/bin/activate
pyinstaller --noconfirm gui_linux.spec
cp -r src/img ./dist/SeaGapDockerGUI/img/
