@echo off
cmd /k "cd /d %~dp0 && venv\Scripts\activate && python manage.py runserver"