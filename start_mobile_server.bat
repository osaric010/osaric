@echo off
echo ========================================
echo       تشغيل خادم أوساريك للهواتف
echo ========================================
echo.

echo تشغيل خادم Django...
start "Django Server" cmd /k "cd /d D:\osama && python manage.py runserver 0.0.0.0:8000"

echo.
echo انتظر 5 ثوان لتشغيل الخادم...
timeout /t 5 /nobreak > nul

echo.
echo تشغيل ngrok...
echo ملاحظة: تأكد من وجود ngrok.exe في نفس المجلد أو في PATH
echo.

if exist ngrok.exe (
    echo تم العثور على ngrok، جاري التشغيل...
    ngrok.exe http 8000
) else (
    echo ngrok غير موجود في هذا المجلد
    echo يرجى تحميل ngrok من: https://ngrok.com/download
    echo ووضع ngrok.exe في نفس مجلد هذا الملف
    echo.
    echo أو تشغيل الأمر التالي يدوياً:
    echo ngrok http 8000
    echo.
    pause
)

pause
