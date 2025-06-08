# دليل النشر السريع - نظام حسابات أوساريك
# Quick Deployment Guide - Osaric Accounts System

## 🚀 خيارات النشر السريع

### 1. النشر على Heroku (مجاني)

```bash
# تثبيت Heroku CLI
# تسجيل الدخول
heroku login

# إنشاء تطبيق جديد
heroku create osaric-accounts-[your-name]

# إضافة قاعدة البيانات
heroku addons:create heroku-postgresql:mini

# إضافة Redis
heroku addons:create heroku-redis:mini

# تعيين متغيرات البيئة
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
heroku config:set DJANGO_SETTINGS_MODULE=osaric_accounts.settings_production_secure

# نشر التطبيق
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# تطبيق قاعدة البيانات
heroku run python manage.py migrate
heroku run python manage.py createsuperuser

# فتح التطبيق
heroku open
```

**الرابط:** `https://osaric-accounts-[your-name].herokuapp.com`

---

### 2. النشر على Railway (سهل ومجاني)

```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# إنشاء مشروع جديد
railway new

# ربط المشروع
railway link

# إضافة قاعدة البيانات
railway add postgresql
railway add redis

# نشر التطبيق
railway up

# الحصول على الرابط
railway domain
```

**الرابط:** `https://[project-name].up.railway.app`

---

### 3. النشر على Render (مجاني مع قاعدة بيانات)

1. **إنشاء حساب على Render.com**
2. **ربط مستودع GitHub**
3. **إنشاء Web Service جديد**
4. **إعدادات التطبيق:**
   - Build Command: `pip install -r requirements_production.txt`
   - Start Command: `gunicorn osaric_accounts.wsgi:application`
   - Environment: `Python 3`

5. **إضافة قاعدة البيانات PostgreSQL**
6. **تعيين متغيرات البيئة:**
   ```
   DEBUG=False
   SECRET_KEY=[generated-key]
   DATABASE_URL=[from-database]
   ```

**الرابط:** `https://[app-name].onrender.com`

---

### 4. النشر على DigitalOcean App Platform

```bash
# إنشاء ملف .do/app.yaml
mkdir .do
cat > .do/app.yaml << EOF
name: osaric-accounts
services:
- name: web
  source_dir: /
  github:
    repo: [your-username]/osaric-accounts
    branch: main
  run_command: gunicorn osaric_accounts.wsgi:application
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    type: SECRET
databases:
- name: osaric-db
  engine: PG
  version: "13"
EOF

# نشر باستخدام doctl CLI
doctl apps create .do/app.yaml
```

**الرابط:** `https://[app-name]-[hash].ondigitalocean.app`

---

### 5. النشر على خادم VPS (Ubuntu)

```bash
# تحميل سكريبت التثبيت
wget https://raw.githubusercontent.com/[your-repo]/osaric-accounts/main/install_production.sh

# تشغيل السكريبت
chmod +x install_production.sh
sudo ./install_production.sh

# اتباع التعليمات التفاعلية
```

**الرابط:** `https://your-domain.com`

---

### 6. النشر باستخدام Docker

```bash
# إنشاء ملف .env
cp .env.production .env

# تعديل المتغيرات
nano .env

# بناء وتشغيل الحاويات
docker-compose up -d --build

# تطبيق قاعدة البيانات
docker-compose exec web python manage.py migrate

# إنشاء مستخدم إداري
docker-compose exec web python manage.py createsuperuser
```

**الرابط:** `http://localhost:8000`

---

## 🔗 الروابط الموثقة المتاحة

### الروابط المجانية:
1. **Heroku:** `https://osaric-accounts-[name].herokuapp.com`
2. **Railway:** `https://[project].up.railway.app`
3. **Render:** `https://[app].onrender.com`
4. **Vercel:** `https://[app].vercel.app`
5. **Netlify:** `https://[app].netlify.app`

### الروابط المدفوعة:
1. **DigitalOcean:** `https://[app].ondigitalocean.app`
2. **AWS:** `https://[app].elasticbeanstalk.com`
3. **Google Cloud:** `https://[app].appspot.com`
4. **Azure:** `https://[app].azurewebsites.net`

---

## 🛡️ إعدادات الأمان للإنتاج

### 1. متغيرات البيئة المطلوبة:
```bash
DEBUG=False
SECRET_KEY=[strong-secret-key]
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_PASSWORD=[strong-password]
EMAIL_HOST_PASSWORD=[app-password]
```

### 2. شهادة SSL:
- **Let's Encrypt:** مجانية
- **Cloudflare:** مجانية مع CDN
- **AWS Certificate Manager:** مجانية

### 3. النطاق المخصص:
```bash
# شراء نطاق من:
- Namecheap: $8-15/سنة
- GoDaddy: $10-20/سنة
- Cloudflare: $8-12/سنة

# إعداد DNS:
A Record: @ -> [server-ip]
CNAME: www -> your-domain.com
```

---

## 📊 مقارنة خيارات الاستضافة

| المنصة | التكلفة | سهولة النشر | الأداء | الدعم |
|--------|---------|-------------|---------|--------|
| Heroku | مجاني/مدفوع | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Railway | مجاني/مدفوع | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Render | مجاني/مدفوع | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| DigitalOcean | مدفوع | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| VPS | مدفوع | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 🎯 التوصيات

### للمبتدئين:
- **Railway** أو **Render** - سهل ومجاني

### للمشاريع الصغيرة:
- **Heroku** - موثوق ومستقر

### للمشاريع الكبيرة:
- **DigitalOcean** أو **AWS** - أداء عالي

### للتحكم الكامل:
- **VPS** مع Ubuntu - مرونة كاملة

---

## 📞 الدعم والمساعدة

- **الوثائق:** https://docs.osaric.com
- **المجتمع:** https://community.osaric.com
- **الدعم:** support@osaric.com
- **GitHub:** https://github.com/osaric/accounts

---

## ✅ قائمة التحقق بعد النشر

- [ ] التطبيق يعمل بدون أخطاء
- [ ] قاعدة البيانات متصلة
- [ ] الملفات الثابتة تظهر بشكل صحيح
- [ ] شهادة SSL مفعلة
- [ ] المستخدم الإداري يعمل
- [ ] النسخ الاحتياطي مجدول
- [ ] السجلات تعمل بشكل صحيح
- [ ] الأمان مفعل
- [ ] الأداء مقبول
- [ ] النطاق المخصص يعمل
