#!/bin/bash

# سكريبت النشر التلقائي لنظام حسابات أوساريك
# Automated deployment script for Osaric Accounts System

set -e

echo "🚀 بدء عملية النشر..."
echo "🚀 Starting deployment process..."

# تحديد المتغيرات
PROJECT_NAME="osaric_accounts"
PROJECT_DIR="/opt/$PROJECT_NAME"
VENV_DIR="/opt/${PROJECT_NAME}_env"
BACKUP_DIR="/var/backups/$PROJECT_NAME"
NGINX_CONFIG="/etc/nginx/sites-available/$PROJECT_NAME"
SYSTEMD_SERVICE="/etc/systemd/system/$PROJECT_NAME.service"

# إنشاء نسخة احتياطية
echo "📦 إنشاء نسخة احتياطية..."
if [ -d "$PROJECT_DIR" ]; then
    sudo cp -r "$PROJECT_DIR" "$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S)"
fi

# تحديث الكود
echo "📥 تحديث الكود..."
if [ -d "$PROJECT_DIR/.git" ]; then
    cd "$PROJECT_DIR"
    sudo git pull origin main
else
    sudo git clone https://github.com/yourusername/osaric-accounts.git "$PROJECT_DIR"
fi

# تفعيل البيئة الافتراضية
echo "🔧 تفعيل البيئة الافتراضية..."
source "$VENV_DIR/bin/activate"

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
cd "$PROJECT_DIR"
pip install -r requirements_production.txt

# تطبيق التحديثات على قاعدة البيانات
echo "🗄️ تطبيق تحديثات قاعدة البيانات..."
python manage.py migrate --noinput

# جمع الملفات الثابتة
echo "📁 جمع الملفات الثابتة..."
python manage.py collectstatic --noinput

# إعادة تشغيل الخدمات
echo "🔄 إعادة تشغيل الخدمات..."
sudo systemctl restart "$PROJECT_NAME"
sudo systemctl restart nginx

# التحقق من حالة الخدمات
echo "✅ التحقق من حالة الخدمات..."
if sudo systemctl is-active --quiet "$PROJECT_NAME"; then
    echo "✅ خدمة $PROJECT_NAME تعمل بنجاح"
else
    echo "❌ خطأ في خدمة $PROJECT_NAME"
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    echo "✅ خدمة Nginx تعمل بنجاح"
else
    echo "❌ خطأ في خدمة Nginx"
    exit 1
fi

# تنظيف النسخ الاحتياطية القديمة
echo "🧹 تنظيف النسخ الاحتياطية القديمة..."
find "$BACKUP_DIR" -name "backup_*" -mtime +7 -exec rm -rf {} \;

echo "🎉 تم النشر بنجاح!"
echo "🌐 الموقع متاح على: https://your-domain.com"
echo "🎉 Deployment completed successfully!"
