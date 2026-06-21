@echo off
REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start Flask backend
start cmd /k "python -m flask run --port 5000"

REM Change directory to web and start Next.js dev server
cd web
start cmd /k "npm run dev"
