@echo off
echo ========================================
echo Starting Celery Beat (Scheduler)
echo ========================================
echo.

cd /d "%~dp0"
python -m celery -A backend.tasks.celery_config beat --loglevel=info

pause

