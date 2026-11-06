@echo off
rem ==========================================================
rem  Smart Health Tracker - opens the graphical launcher
rem  Run "SmartHealth.bat debug" to see errors in a console.
rem ==========================================================
title Smart Health Tracker
cd /d "%~dp0"
set "PY="

if /i "%~1"=="debug" goto debug

where pythonw >nul 2>nul && set "PY=pythonw"
if not defined PY where pyw >nul 2>nul && set "PY=pyw -3"
if not defined PY goto nopython
start "" %PY% "%~dp0launcher.py"
exit /b 0

:debug
where python >nul 2>nul && set "PY=python"
if not defined PY where py >nul 2>nul && set "PY=py -3"
if not defined PY goto nopython
%PY% "%~dp0launcher.py"
pause
exit /b 0

:nopython
echo.
echo  Python was not found on this computer.
echo.
echo  Please install Python 3.12 from https://www.python.org/downloads/
echo  and tick "Add Python to PATH" during the installation.
echo.
start "" https://www.python.org/downloads/
pause
exit /b 1
