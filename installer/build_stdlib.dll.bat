@echo off
%~d0
cd %~dp0
@echo on
..\bin\ipy.exe -m bkt_install.build_stdlib
pause