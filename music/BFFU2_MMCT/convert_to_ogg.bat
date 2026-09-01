@echo off
set FFMPEG="C:\Users\Roberts (ME)\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe"

if "%~1"=="" (
    echo Drag and drop a WAV or MP3 file onto this script to convert it to OGG.
    pause
    exit /b
)

for %%F in (%*) do (
    echo Converting %%~nF to OGG...
    %FFMPEG% -y -i "%%~F" "%%~dpnF.ogg"
)

echo Done!
pause
