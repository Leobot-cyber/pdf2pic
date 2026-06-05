@echo off
setlocal

echo ========================================
echo   PDF转图片 - 一键构建安装程序
echo ========================================
echo.

call "%~dp0build.bat"
if errorlevel 1 (
    echo [错误] 程序打包失败
    exit /b 1
)

call "%~dp0build_installer.bat"
if errorlevel 1 (
    echo [错误] 安装程序构建失败
    exit /b 1
)

echo.
echo ========================================
echo   全部完成！
echo   安装包: installer\output\PdfToPic_Setup_1.0.0.exe
echo ========================================

endlocal
