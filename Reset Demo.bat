@echo off
setlocal
cd /d "%~dp0"
echo This removes the MinIO data, the Nessie catalog, the MLflow database and Dremio data.
choice /C YN /M "Continue with a full reset"
if errorlevel 2 exit /b 0
docker compose --profile dremio down -v --remove-orphans
echo.
echo Reset complete. Start Demo.bat will build a fresh lakehouse.
pause
