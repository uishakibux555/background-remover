@echo off
setlocal
:: Change directory to the script location to ensure imports work
cd /d "%~dp0"

echo ========================================================
echo              Shakib's Background Remover Tool
echo ========================================================
echo.
:: Check if a file was dragged onto the script
:: Check if a file was dragged onto the script (check first argument)
if "%~1" neq "" (
    :: If dragged, we want to pass ALL args (%*) to the variable
    :: We save them and pass them after user selects the tool
    set "InputArgs=%*"
    goto :InteractiveLoop
)

:InteractiveLoop
echo.
echo ========================================================
echo                 SELECT TOOL
echo ========================================================
echo 1. Background Remover (Standard - U2Net)
echo 2. Background Remover (Advanced - SAM 2.1)
echo 3. Background Remover (BiRefNet - SOTA)
echo 4. Background Remover (RMBG-2.0 - New)
echo ========================================================
set /p "ToolChoice=Enter choice (1-4): "

if "%ToolChoice%"=="4" goto :RMBG2Flow
if "%ToolChoice%"=="3" goto :BiRefNetFlow
if "%ToolChoice%"=="2" goto :SAMFlow
if "%ToolChoice%"=="1" goto :RemoverFlow

echo Invalid choice. Defaulting to Standard Remover.
goto :RemoverFlow

:RMBG2Flow
if defined InputArgs goto :RMBG2UseArgs

echo.
echo [RMBG-2.0 BACKGROUND REMOVER]
echo Please drag and drop your image file(s) into this window 
echo and press Enter.
set "TargetFiles="
set /p "TargetFiles=> "
goto :RMBG2Run

:RMBG2UseArgs
set "TargetFiles=%InputArgs%"

:RMBG2Run
if not defined TargetFiles goto :InteractiveLoop

echo.
echo Processing with RMBG-2.0...
py -3.13 rmbg2_remover.py -i %TargetFiles%
goto :Done

:BiRefNetFlow
if defined InputArgs goto :BiRefNetUseArgs

echo.
echo [BiRefNet BACKGROUND REMOVER]
echo Please drag and drop your image file(s) into this window 
echo and press Enter.
set "TargetFiles="
set /p "TargetFiles=> "
goto :BiRefNetRun

:BiRefNetUseArgs
set "TargetFiles=%InputArgs%"

:BiRefNetRun
if not defined TargetFiles goto :InteractiveLoop

echo.
echo Processing with BiRefNet (State of the Art)...
py -3.13 birefnet_remover.py -i %TargetFiles%
goto :Done

:SAMFlow
if defined InputArgs goto :SAMUseArgs

echo.
echo [SAM 2 BACKGROUND REMOVER]
echo Please drag and drop your image file(s) into this window 
echo and press Enter.
set "TargetFiles="
set /p "TargetFiles=> "
goto :SAMRun

:SAMUseArgs
set "TargetFiles=%InputArgs%"

:SAMRun
if not defined TargetFiles goto :InteractiveLoop

echo.
echo Processing with SAM 2...
py -3.13 sam2_remover.py -i %TargetFiles%
goto :Done

:RemoverFlow
if defined InputArgs goto :RemoverUseArgs

echo.
echo [STANDARD REMOVER - U2NET]
echo Please drag and drop your image file(s) into this window 
echo and press Enter.
set "TargetFiles="
set /p "TargetFiles=> "
goto :RemoverRun

:RemoverUseArgs
set "TargetFiles=%InputArgs%"

:RemoverRun
if not defined TargetFiles goto :InteractiveLoop

echo.
echo Processing...
py -3.13 background_remover.py -i %TargetFiles%
goto :Done

:UpscaleFlow
echo.
echo [IMAGE UPSCALER]

:: Ask for scale factor
echo Select Upscale Factor:
echo 1. 1x (Enhance details only)
echo 2. 2x (Double size)
echo 4. 4x (Quadruple size - Default)
set /p "ScaleChoice=Enter choice (1, 2, or 4): "

:: Default to 4 if invalid
if "%ScaleChoice%"=="" set "ScaleChoice=4"
if "%ScaleChoice%"=="3" set "ScaleChoice=4"

if defined InputArgs goto :UpscaleUseArgs

echo.
echo Please drag and drop your image file(s) into this window 
echo and press Enter.
set "TargetFiles="
set /p "TargetFiles=> "
goto :UpscaleRun

:UpscaleUseArgs
set "TargetFiles=%InputArgs%"

:UpscaleRun
if not defined TargetFiles goto :InteractiveLoop

echo.
echo Processing with Scale %ScaleChoice%x...
py -3.13 upscaler.py -i %TargetFiles% -s %ScaleChoice%
goto :Done


:Done
:: Clear args after one run so loop works correctly
set "InputArgs="

echo.
echo ========================================================
if %errorlevel% equ 0 (
    echo.
    echo               DONE! 
    echo Check the folders of your images for the output files.
) else (
    echo.
    echo               ERROR OCCURRED
    echo.
    echo If you see 'ModuleNotFoundError', the script attempts to auto-install.
    echo Please try running it again if it installed dependencies.
)

echo.
echo Press any key to start a new task...
pause >nul
goto :InteractiveLoop
