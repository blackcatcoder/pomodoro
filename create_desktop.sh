#!/bin/bash
path=$(pwd)

echo "[Desktop Entry]
Type=Application
Version=1.0
Name=Timer
Comment=A simple pomodoro timer
Path=$path
Exec=python pomodoro.py
Icon=$path/icons/icon.png
Categories=Other;
Terminal=false;
Name[en_IN.utf8]=Promodoro">Promodoro.desktop

chmod +x Promodoro.desktop
