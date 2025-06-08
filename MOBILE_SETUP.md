# 📱 دليل تشغيل التطبيق على الهاتف المحمول

## 🚀 الطريقة الأولى: استخدام ngrok (الأسرع)

### 1. تحميل ngrok
- اذهب إلى: https://ngrok.com/download
- حمل النسخة المناسبة لـ Windows
- فك الضغط عن الملف واحفظ `ngrok.exe` في مجلد المشروع

### 2. تشغيل التطبيق
- شغل الملف: `start_mobile_server.bat`
- أو شغل الأوامر التالية يدوياً:

```bash
# تشغيل خادم Django
python manage.py runserver 0.0.0.0:8000

# في نافذة أخرى، تشغيل ngrok
ngrok http 8000
```

### 3. الحصول على الرابط
- ستحصل على رابط مثل: `https://abc123.ngrok.io`
- استخدم هذا الرابط على الهاتف من أي مكان في العالم

---

## 🌐 الطريقة الثانية: النشر على Heroku (دائم ومجاني)

### 1. إنشاء حساب Heroku
- اذهب إلى: https://heroku.com
- أنشئ حساب مجاني

### 2. تثبيت Heroku CLI
- حمل من: https://devcenter.heroku.com/articles/heroku-cli
- ثبت البرنامج

### 3. تحضير المشروع
```bash
# تسجيل الدخول إلى Heroku
heroku login

# إنشاء تطبيق جديد
heroku create your-app-name

# إضافة قاعدة بيانات PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# رفع الكود
git init
git add .
git commit -m "Initial commit"
git push heroku main

# تشغيل migrations
heroku run python manage.py migrate

# إنشاء superuser
heroku run python manage.py createsuperuser
```

### 4. الحصول على الرابط
- ستحصل على رابط مثل: `https://your-app-name.herokuapp.com`

---

## 🚄 الطريقة الثالثة: Railway (سهل وسريع)

### 1. إنشاء حساب
- اذهب إلى: https://railway.app
- أنشئ حساب باستخدام GitHub

### 2. رفع الكود إلى GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/osaric-accounts.git
git push -u origin main
```

### 3. النشر من Railway
- اختر "Deploy from GitHub repo"
- اختر المستودع
- Railway سيقوم بالنشر تلقائياً

---

## 🎯 الطريقة الرابعة: Render (مجاني)

### 1. إنشاء حساب
- اذهب إلى: https://render.com
- أنشئ حساب مجاني

### 2. إنشاء Web Service
- اختر "New Web Service"
- اربط GitHub repository
- استخدم الإعدادات التالية:
  - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
  - Start Command: `gunicorn osaric_accounts.wsgi:application`

---

## 📱 إضافة التطبيق للشاشة الرئيسية

### على Android:
1. افتح الرابط في Chrome
2. اضغط على القائمة (⋮)
3. اختر "إضافة إلى الشاشة الرئيسية"
4. اكتب اسم التطبيق واضغط "إضافة"

### على iPhone/iPad:
1. افتح الرابط في Safari
2. اضغط على زر المشاركة (□↗)
3. اختر "إضافة إلى الشاشة الرئيسية"
4. اكتب اسم التطبيق واضغط "إضافة"

---

## 🔧 نصائح مهمة

### للأمان:
- غير `SECRET_KEY` في الإنتاج
- اضبط `DEBUG = False` في الإنتاج
- حدد `ALLOWED_HOSTS` بدقة

### للأداء:
- استخدم قاعدة بيانات PostgreSQL في الإنتاج
- فعل ضغط الملفات الثابتة
- استخدم CDN للملفات الكبيرة

### للصيانة:
- احتفظ بنسخة احتياطية من قاعدة البيانات
- راقب استخدام الموارد
- حدث التطبيق بانتظام

---

## 🆘 حل المشاكل الشائعة

### خطأ "Application Error":
```bash
heroku logs --tail
```

### خطأ في قاعدة البيانات:
```bash
heroku run python manage.py migrate
```

### خطأ في الملفات الثابتة:
```bash
heroku run python manage.py collectstatic --noinput
```

### إعادة تشغيل التطبيق:
```bash
heroku restart
```

---

## 📞 الدعم

إذا واجهت أي مشاكل:
1. تحقق من logs التطبيق
2. تأكد من صحة إعدادات قاعدة البيانات
3. تحقق من متغيرات البيئة
4. راجع وثائق المنصة المستخدمة
