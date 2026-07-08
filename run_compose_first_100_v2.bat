@echo off
chcp 65001 >nul
echo ============================================================
echo   NO REFUNDS ARCHIVE - First 100 Composition v2
echo   Pipeline: Plan → Validate → Compose → Check
echo ============================================================
echo.

echo [1/4] Generating v2 composition plan (100 cards)...
python generate_plan_0100.py
if %errorlevel% neq 0 (
    echo ✗ Plan generation failed!
    pause
    exit /b 1
)
echo.

echo [2/4] Validating plan (cross-series checks)...
python validate_compose_plan.py --csv data/auto_compose_plan_0100_v2.csv
if %errorlevel% neq 0 (
    echo ✗ Validation found errors! Check report.
    echo.
    echo Report: data/compose_plan_validation_report_v2.csv
    pause
    exit /b 1
)
echo.

echo [3/4] Composing 100 images + metadata v2...
python compose_nra_assets.py --csv data/auto_compose_plan_0100_v2.csv --limit 100
if %errorlevel% neq 0 (
    echo ✗ Composition failed!
    pause
    exit /b 1
)
echo.

echo [4/4] Final validation with file checks...
python validate_compose_plan.py --csv data/auto_compose_plan_0100_v2.csv --files --output data/compose_plan_validation_report_v2.csv
echo.

echo ============================================================
echo   COMPLETE!
echo   Images:    output/final_images_v2/
echo   Metadata:  output/metadata_v2/
echo   Preview:   output/preview_check_0100_v2.csv
echo   Validate:  data/compose_plan_validation_report_v2.csv
echo ============================================================
pause
