@echo off
chcp 65001 >nul
echo ============================================================
echo   NO REFUNDS ARCHIVE - First 100 Batch Composer
echo ============================================================
echo.
echo Step 1: Asset existence check...
python compose_nra_assets.py --csv data/auto_compose_plan_0100.csv --limit 100 --check --preview output/preview_check_0100.csv
echo.
echo Step 2: Composing 100 images...
python compose_nra_assets.py --csv data/auto_compose_plan_0100.csv --limit 100 --preview output/preview_check_0100.csv
echo.
echo ============================================================
echo   DONE! Check output/final_images/ and output/metadata/
echo ============================================================
pause
