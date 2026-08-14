@echo off
REM ============================================================
REM  Refresh the LOCAL BFFU test mod ("uk-rework" folder) from
REM  git main, then enable "BFFU 2 (Local)" in the HOI4 launcher.
REM
REM  This stamps a LOCAL descriptor with NO remote_file_id, so it
REM  never clashes with the subscribed Workshop BFFU 2 (3765324616).
REM  The original item (3745245470) was taken down and is no longer used.
REM  To PUBLISH to the Workshop instead, run upload-bffu.bat.
REM ============================================================
setlocal
set "HUB=C:\Users\Roberts (ME)\Documents\GitHub\BFFU-DEV"
set "DEST=C:\Users\Roberts (ME)\Documents\Paradox Interactive\Hearts of Iron IV\mod\uk-rework"
set "MODFILE=C:\Users\Roberts (ME)\Documents\Paradox Interactive\Hearts of Iron IV\mod\uk-rework.mod"

echo Refreshing the local "BFFU 2 (Local)" test mod from git main...
cd /d "%HUB%"

if exist "%DEST%" rmdir /s /q "%DEST%"
mkdir "%DEST%"

git archive --format=tar main | tar -x -C "%DEST%"
if errorlevel 1 (
    echo.
    echo ERROR: export failed. Make sure git is installed and "main" exists.
    pause
    exit /b 1
)

REM Strip dev-only files/folders that must NOT ship, even if git ever tracks them.
del /q "%DEST%\publish-bffu.bat" 2>nul
del /q "%DEST%\upload-bffu.bat" 2>nul
del /q "%DEST%\.gitignore" 2>nul
del /q "%DEST%\.gitattributes" 2>nul
if exist "%DEST%\.claude" rmdir /s /q "%DEST%\.claude"
if exist "%DEST%\.codebuddy" rmdir /s /q "%DEST%\.codebuddy"
del /q "%DEST%\changelog.txt" 2>nul

REM --- LOCAL folder descriptor (no remote_file_id) ---
call :write_descriptor "%DEST%\descriptor.mod" "BFFU 2 (Local)"

REM --- LOCAL launcher pointer (adds path, still no remote_file_id) ---
call :write_descriptor "%MODFILE%" "BFFU 2 (Local)"
>> "%MODFILE%" echo path="C:/Users/Roberts (ME)/Documents/Paradox Interactive/Hearts of Iron IV/mod/uk-rework"

echo.
echo Done. In the launcher, enable "BFFU 2 (Local)" to test the latest main.
echo (To publish to the Workshop instead, run upload-bffu.bat.)
pause
exit /b 0

:write_descriptor
REM %~1 = target .mod file, %~2 = mod name
> "%~1" echo version="1.19"
>> "%~1" echo tags={
>> "%~1" echo 	"Balance"
>> "%~1" echo 	"Events"
>> "%~1" echo 	"Gameplay"
>> "%~1" echo 	"Historical"
>> "%~1" echo 	"National Focuses"
>> "%~1" echo 	"Technologies"
>> "%~1" echo }
>> "%~1" echo name="%~2"
>> "%~1" echo picture="thumbnail.png"
>> "%~1" echo replace_path="common/ai_equipment"
>> "%~1" echo replace_path="common/ai_strategy"
>> "%~1" echo replace_path="common/ai_strategy_plans"
>> "%~1" echo replace_path="common/ai_templates"
>> "%~1" echo replace_path="gfx/interface/equipmentdesigner/tanks/designer"
>> "%~1" echo replace_path="history/countries"
>> "%~1" echo supported_version="1.19.*"
exit /b 0
