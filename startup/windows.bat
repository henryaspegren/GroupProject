@echo off
set /p id="Enter SRCF user name: "
putty.exe -L 3307:localhost:3306 %id%@shell.srcf.net