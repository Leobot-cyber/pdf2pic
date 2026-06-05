@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   PDF转图片 - Windows 构建脚本
echo ========================================

where python >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    exit /b 1
)

if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo 安装依赖...
python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist "assets\icon.ico" (
    echo 生成应用图标...
    python scripts\generate_icon.py
)

set ARCH=%PROCESSOR_ARCHITECTURE%
if /I "%ARCH%"=="AMD64" (
    set BUILD_ARCH=x64
) else (
    set BUILD_ARCH=x86
)

echo.
echo 当前系统架构: %BUILD_ARCH%
echo 开始 PyInstaller 打包...
echo.

pyinstaller --noconfirm --clean pdfToPic.spec

if errorlevel 1 (
    echo [错误] 打包失败
    exit /b 1
)

if not exist "dist\%BUILD_ARCH%" mkdir "dist\%BUILD_ARCH%"
xcopy /E /I /Y "dist\PdfToPic" "dist\%BUILD_ARCH%\PdfToPic"

echo.
echo ========================================
echo   构建完成: dist\%BUILD_ARCH%\PdfToPic\
echo ========================================
echo.
echo 如需生成安装程序，请安装 Inno Setup 后运行:
echo   build_installer.bat
echo.

endlocal
