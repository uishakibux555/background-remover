@echo off
REM Wrapper script to ensure the correct Python version (3.13) is used.
REM Usage: run.bat -i <input_image> [-o <output_image>]

py -3.13 "%~dp0background_remover.py" %*

if %errorlevel% neq 0 (
    echo.
    echo ----------------------------------------------------------------
    echo Execution failed or no arguments provided.
    echo.
    echo Usage Example:
    echo   .\run.bat -i image.jpg
    echo.
    echo Note: This script uses 'py -3.13' to ensure compatibility.
    echo ----------------------------------------------------------------
    REM Pause only if it wasn't a successful run, so the user can read the error.
    pause
)
