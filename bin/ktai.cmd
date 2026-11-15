@echo off
rem KTAI launcher for Windows - the ktai command (mirrors bin/ktai).
rem Resolves its own directory so a copy in a bin dir on PATH still works.
rem Pure ASCII on purpose: cmd.exe mis-parses UTF-8 bytes under chcp 65001.
setlocal
set "KTAI_ROOT=%~dp0.."
for %%I in ("%KTAI_ROOT%") do set "KTAI_ROOT=%%~fI"
if "%KTAI_HOME%"=="" set "KTAI_HOME=%USERPROFILE%\.ktai"
set "HERMES_HOME=%KTAI_HOME%"
set "PYTHONPATH="
set "PYTHONHOME="
"%KTAI_ROOT%\venv\Scripts\python.exe" "%KTAI_ROOT%\bin\ktai_entry.py" %*
exit /b %ERRORLEVEL%
