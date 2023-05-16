@echo off
color 60
title Workflow321 Installer
echo Installing Workflow321

pyrevit extend ui Workflow321 "https://github.com/dezindzer/Workflow321.git" --branch=main &cls

echo Installation done
timeout 3 
echo done