#!/bin/bash

# سكريبت بدء Docker لنظام حسابات أوساريك
# Docker entrypoint script for Osaric Accounts System

set -e

# انتظار قاعدة البيانات
echo "انتظار قاعدة البيانات..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "قاعدة البيانات متاحة!"

# تطبيق التحديثات على قاعدة البيانات
echo "تطبيق تحديثات قاعدة البيانات..."
python manage.py migrate --noinput

# إنشاء مستخدم إداري إذا لم يكن موجوداً
echo "التحقق من المستخدم الإداري..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@osaric.com', 'admin123')
    print('تم إنشاء مستخدم إداري')
else:
    print('المستخدم الإداري موجود')
"

# تطبيق إعدادات النظام
echo "تطبيق إعدادات النظام..."
python manage.py apply_system_settings || true

# جمع الملفات الثابتة
echo "جمع الملفات الثابتة..."
python manage.py collectstatic --noinput

echo "بدء التطبيق..."
exec "$@"
