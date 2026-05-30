@echo off
chcp 65001 >nul
title E-Learning Launcher
echo ============================================
echo   E-LEARNING - KHOI DONG HE THONG
echo ============================================
echo.

REM 1. Mo cong qua USB cho dien thoai (neu co cam may)
echo [1/3] Mo cong 8000 qua USB (adb reverse)...
"C:\Users\ASUS\AppData\Local\Android\sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000 2>nul
if %errorlevel%==0 (
  echo     -^> OK: dien thoai co the goi 127.0.0.1:8000
) else (
  echo     -^> Khong thay dien thoai USB ^(van chay binh thuong^)
)
echo.

REM 2. Chay AI service (RAG + Qdrant + LangGraph) o cua so rieng - cong 8100
echo [2/3] Mo AI service (RAG) o cua so rieng - cong 8100...
start "E-Learning AI Service (8100)" cmd /k "chcp 65001 >nul && cd /d C:\Users\ASUS\elearning_app\ai_service && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8100"
echo     -^> Da mo. Lan dau co the mat ~10-20s de nap model.
echo.

REM 3. Chay backend chinh o cua so nay - cong 8000
echo [3/3] Dang chay backend tai http://127.0.0.1:8000 ...
echo     ^(Nhan Ctrl+C de dung backend. AI service o cua so kia dong rieng.^)
echo.
cd /d "C:\Users\ASUS\elearning_app\backend"
".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
