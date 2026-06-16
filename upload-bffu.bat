@echo off
REM ============================================================
REM  Publish BFFU to the Steam Workshop (item 3745245470).
REM  Exports git main into the MAIN BRANCH folder and stamps the
REM  UPLOAD identity (name="BFFU", remote_file_id=3745245470), then
REM  you upload it from the HOI4 launcher.
REM
REM  IMPORTANT: before uploading, DISABLE/unsubscribe the Workshop
REM  "BFFU" in the launcher, or its remote_file_id will clash with
REM  this folder. After uploading, run publish-bffu.bat to put
REM  MAIN BRANCH back to its local "BFFU (Local)" descriptor.
REM ============================================================
setlocal
set "HUB=C:\Users\Roberts (ME)\Documents\GitHub\Secret Rearmament"
set "DEST=C:\Users\Roberts (ME)\Documents\Paradox Interactive\Hearts of Iron IV\mod\MAIN BRANCH"
set "MODFILE=C:\Users\Roberts (ME)\Documents\Paradox Interactive\Hearts of Iron IV\mod\MAIN BRANCH.mod"

echo Re-exporting "BFFU" (main) for Workshop upload...
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

REM Strip dev-only files that git tracks but must NOT ship to the Workshop.
del /q "%DEST%\publish-bffu.bat" 2>nul
del /q "%DEST%\upload-bffu.bat" 2>nul
del /q "%DEST%\.gitignore" 2>nul
del /q "%DEST%\.gitattributes" 2>nul

REM git main's descriptor.mod already carries the UPLOAD identity
REM (name="BFFU", remote_file_id="3745245470"), so the folder is ready.
REM Stamp the matching UPLOAD launcher pointer (root .mod).
call :write_descriptor "%MODFILE%" "BFFU"
>> "%MODFILE%" echo path="C:/Users/Roberts (ME)/Documents/Paradox Interactive/Hearts of Iron IV/mod/MAIN BRANCH"
>> "%MODFILE%" echo remote_file_id="3745245470"

echo.
echo Done. 1) DISABLE the subscribed Workshop "BFFU" in the launcher.
echo       2) Upload "BFFU" from the launcher (updates item 3745245470).
echo       3) Run publish-bffu.bat afterwards to restore "BFFU (Local)".
pause
exit /b 0

:write_descriptor
REM %~1 = target .mod file, %~2 = mod name
> "%~1" echo version="1.17.3.0"
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
>> "%~1" echo supported_version="1.17.3.0"
exit /b 0
