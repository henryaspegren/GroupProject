@echo off
set /p id="Enter remote user name: "
set /p dest="Enter remote machine: "
putty.exe -L 3307:localhost:3306 %id%@%dest%