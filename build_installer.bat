@echo off
setlocal

echo ========================================
echo   PDF转图片 - 安装程序构建
echo ========================================

set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "%ISCC%"=="" (
    echo [错误] 未找到 Inno Setup 6，请先安装:
    echo https://jrsoftware.org/isdl.php
    exit /b 1
)

set STAGING=installer\staging
if exist "%STAGING%" rmdir /S /Q "%STAGING%"
mkdir "%STAGING%"

set ARCH=%PROCESSOR_ARCHITECTURE%
if /I "%ARCH%"=="AMD64" set PREFERRED=x64
if /I not "%ARCH%"=="AMD64" set PREFERRED=x86

set SOURCE=
if exist "dist\%PREFERRED%\PdfToPic\PdfToPic.exe" (
    set SOURCE=dist\%PREFERRED%\PdfToPic
)
if "%SOURCE%"=="" if exist "dist\x64\PdfToPic\PdfToPic.exe" set SOURCE=dist\x64\PdfToPic
if "%SOURCE%"=="" if exist "dist\x86\PdfToPic\PdfToPic.exe" set SOURCE=dist\x86\PdfToPic
if "%SOURCE%"=="" if exist "dist\PdfToPic\PdfToPic.exe" set SOURCE=dist\PdfToPic

if "%SOURCE%"=="" (
    echo [错误] 未找到构建产物，请先运行 build.bat
    exit /b 1
)

echo 使用构建产物: %SOURCE%
xcopy /E /I /Y "%SOURCE%\*" "%STAGING%\"

if not exist "assets\icon.ico" (
    echo 生成应用图标...
    call venv\Scripts\activate.bat 2>nul
    python scripts\generate_icon.py
)

if not exist "installer\output" mkdir "installer\output"

"%ISCC%" "installer\setup.iss"

if errorlevel 1 (
    echo [错误] 安装程序构建失败
    exit /b 1
)

echo.
echo ========================================
echo   安装程序: installer\output\PdfToPic_Setup_1.0.0.exe
echo ========================================

endlocal
