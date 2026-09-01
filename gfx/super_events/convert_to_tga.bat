@echo off
set FFMPEG="C:\Users\Roberts (ME)\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"

if "%~1"=="" (
    echo Drag and drop a PNG or JPG file onto this script to convert it to TGA.
    pause
    exit /b
)

for %%F in (%*) do (
    echo Converting %%~nF to TGA...
    %FFMPEG% -y -i "%%~F" "%%~dpnF.tga"
)

echo Done!
pause
