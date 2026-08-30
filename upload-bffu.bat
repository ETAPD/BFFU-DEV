@echo off
REM ============================================================
REM  Publish BFFU 2 to the Steam Workshop (item 3765324616).
REM  The original item (3745245470) was taken down, so this is a
REM  fresh Workshop item under the name "BFFU 2".
REM  Exports git main into the uk-rework folder and stamps the
REM  UPLOAD identity (name="BFFU 2", remote_file_id=3765324616),
REM  then you upload it from the HOI4 launcher.
REM
REM  IMPORTANT: before uploading, DISABLE/unsubscribe any other
REM  local copy of BFFU/BFFU 2 in the launcher, or it will clash
REM  with this folder. After uploading, run publish-bffu.bat to
REM  put uk-rework back to its local "BFFU 2 (Local)" descriptor.
REM ============================================================
setlocal
set "HUB=C:\Users\Roberts (ME)\Documents\GitHub\BFFU-DEV"
set "DEST=C:\Users\Roberts (ME)\Documents\Paradox Interactive\Hearts of Iron IV\mod\uk-rework"
set "MODFILE=C:\Users\Roberts (ME)\Documents\Paradox Interactive\Hearts of Iron IV\mod\uk-rework.mod"

echo Re-exporting "BFFU 2" (main) for Workshop upload...
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

REM Strip dev-only files/folders that must NOT ship to the Workshop.
del /q "%DEST%\publish-bffu.bat" 2>nul
del /q "%DEST%\upload-bffu.bat" 2>nul
del /q "%DEST%\.gitignore" 2>nul
del /q "%DEST%\.gitattributes" 2>nul
if exist "%DEST%\.claude" rmdir /s /q "%DEST%\.claude"
if exist "%DEST%\.codebuddy" rmdir /s /q "%DEST%\.codebuddy"
del /q "%DEST%\changelog.txt" 2>nul

REM Stamp the UPLOAD identity on both the folder descriptor and the
REM launcher pointer - written explicitly here rather than trusting
REM whatever descriptor.mod happens to be checked into main.
call :write_descriptor "%DEST%\descriptor.mod" "BFFU 2"
>> "%DEST%\descriptor.mod" echo remote_file_id="3765324616"

call :write_descriptor "%MODFILE%" "BFFU 2"
>> "%MODFILE%" echo path="C:/Users/Roberts (ME)/Documents/Paradox Interactive/Hearts of Iron IV/mod/uk-rework"
>> "%MODFILE%" echo remote_file_id="3765324616"

echo.
echo Done. 1) DISABLE any other subscribed/local "BFFU" copy in the launcher.
echo       2) Upload "BFFU 2" from the launcher (updates item 3765324616).
echo       3) Run publish-bffu.bat afterwards to restore "BFFU 2 (Local)".
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
>> "%~1" echo replace_path="common/units/names_divisions"
>> "%~1" echo replace_path="common/units/names_ships"
>> "%~1" echo replace_path="common/national_focus"
>> "%~1" echo replace_path="common/decisions"
>> "%~1" echo replace_path="common/decisions/categories"
>> "%~1" echo replace_path="common/technologies"
>> "%~1" echo replace_path="events"
>> "%~1" echo replace_path="common/ai_equipment"
>> "%~1" echo replace_path="common/ai_strategy"
>> "%~1" echo replace_path="common/ai_strategy_plans"
>> "%~1" echo replace_path="common/ai_templates"
>> "%~1" echo replace_path="gfx/interface/equipmentdesigner/tanks/designer"
>> "%~1" echo replace_path="history/countries"
>> "%~1" echo supported_version="1.19.*"
exit /b 0
