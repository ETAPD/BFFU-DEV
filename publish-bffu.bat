@echo off
REM ============================================================
REM  Re-export the main branch to the clean BFFU
REM  upload folder, then you upload it in the HOI4 launcher.
REM  (Workshop item 3745245470)
REM ============================================================
setlocal
set "HUB=C:\Users\Roberts (ME)\Documents\GitHub\Secret Rearmament"
set "DEST=C:\Users\Roberts (ME)\Documents\Paradox Interactive\Hearts of Iron IV\mod\MAIN BRANCH"

echo Re-exporting "BFFU" (main) to the upload folder...
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
del /q "%DEST%\.gitignore" 2>nul
del /q "%DEST%\.gitattributes" 2>nul

echo.
echo Done. Open the HOI4 launcher and upload "BFFU".
pause
