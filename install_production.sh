#!/bin/bash

# سكريبت التثبيت الكامل لنظام حسابات أوساريك
# Complete installation script for Osaric Accounts System

set -e

# ألوان للمخرجات
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# دالة طباعة ملونة
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# التحقق من صلاحيات المدير
if [[ $EUID -ne 0 ]]; then
   print_error "يجب تشغيل هذا السكريبت بصلاحيات المدير (sudo)"
   exit 1
fi

print_header "تثبيت نظام حسابات أوساريك - الإصدار الإنتاجي"

# متغيرات التكوين
DOMAIN_NAME=""
DB_PASSWORD=""
EMAIL=""

# طلب المعلومات من المستخدم
read -p "أدخل اسم النطاق (مثال: osaric.com): " DOMAIN_NAME
read -s -p "أدخل كلمة مرور قاعدة البيانات: " DB_PASSWORD
echo
read -p "أدخل بريدك الإلكتروني: " EMAIL

if [[ -z "$DOMAIN_NAME" || -z "$DB_PASSWORD" || -z "$EMAIL" ]]; then
    print_error "جميع الحقول مطلوبة!"
    exit 1
fi

print_status "بدء التثبيت للنطاق: $DOMAIN_NAME"

# 1. تحديث النظام
print_header "تحديث النظام"
apt update && apt upgrade -y

# 2. تثبيت المتطلبات الأساسية
print_header "تثبيت المتطلبات الأساسية"
apt install -y python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib \
    nginx \
    redis-server \
    git \
    curl \
    wget \
    unzip \
    supervisor \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban \
    logrotate

# 3. إعداد جدار الحماية
print_header "إعداد جدار الحماية"
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 6379  # Redis
ufw allow 5432  # PostgreSQL (محلي فقط)

# 4. إعداد PostgreSQL
print_header "إعداد قاعدة البيانات"
sudo -u postgres createuser --interactive --pwprompt osaric_user || true
sudo -u postgres createdb osaric_accounts_prod -O osaric_user || true

# 5. إعداد Redis
print_header "إعداد Redis"
systemctl enable redis-server
systemctl start redis-server

# 6. إنشاء مستخدم التطبيق
print_header "إنشاء مستخدم التطبيق"
useradd --system --shell /bin/bash --home /opt/osaric_accounts --create-home osaric || true
usermod -a -G www-data osaric

# 7. تحميل الكود
print_header "تحميل كود التطبيق"
cd /opt
if [ -d "osaric_accounts" ]; then
    rm -rf osaric_accounts
fi

# استنساخ المشروع (استبدل بالرابط الصحيح)
git clone https://github.com/yourusername/osaric-accounts.git osaric_accounts
chown -R osaric:www-data /opt/osaric_accounts

# 8. إعداد البيئة الافتراضية
print_header "إعداد البيئة الافتراضية"
sudo -u osaric python3 -m venv /opt/osaric_accounts_env
sudo -u osaric /opt/osaric_accounts_env/bin/pip install --upgrade pip
sudo -u osaric /opt/osaric_accounts_env/bin/pip install -r /opt/osaric_accounts/requirements_production.txt

# 9. إعداد متغيرات البيئة
print_header "إعداد متغيرات البيئة"
cat > /opt/osaric_accounts/.env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=$DOMAIN_NAME,www.$DOMAIN_NAME
DB_NAME=osaric_accounts_prod
DB_USER=osaric_user
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1
EMAIL_HOST_USER=$EMAIL
DOMAIN_NAME=$DOMAIN_NAME
EOF

chown osaric:www-data /opt/osaric_accounts/.env
chmod 600 /opt/osaric_accounts/.env

# 10. تطبيق قاعدة البيانات
print_header "إعداد قاعدة البيانات"
cd /opt/osaric_accounts
sudo -u osaric /opt/osaric_accounts_env/bin/python manage.py migrate
sudo -u osaric /opt/osaric_accounts_env/bin/python manage.py collectstatic --noinput

# 11. إنشاء مستخدم إداري
print_header "إنشاء مستخدم إداري"
sudo -u osaric /opt/osaric_accounts_env/bin/python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '$EMAIL', 'admin123')
    print('تم إنشاء مستخدم إداري: admin/admin123')
"

# 12. إعداد Gunicorn
print_header "إعداد Gunicorn"
cp /opt/osaric_accounts/osaric_accounts.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable osaric_accounts
systemctl start osaric_accounts

# 13. إعداد Nginx
print_header "إعداد Nginx"
cp /opt/osaric_accounts/nginx_config.conf /etc/nginx/sites-available/osaric_accounts
sed -i "s/your-domain.com/$DOMAIN_NAME/g" /etc/nginx/sites-available/osaric_accounts
ln -sf /etc/nginx/sites-available/osaric_accounts /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 14. الحصول على شهادة SSL
print_header "الحصول على شهادة SSL"
certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email $EMAIL

# 15. إعداد النسخ الاحتياطي التلقائي
print_header "إعداد النسخ الاحتياطي"
mkdir -p /var/backups/osaric
cat > /etc/cron.d/osaric-backup << EOF
0 2 * * * osaric /opt/osaric_accounts_env/bin/python /opt/osaric_accounts/manage.py dbbackup
0 3 * * * root find /var/backups/osaric -name "*.backup" -mtime +7 -delete
EOF

# 16. إعداد السجلات
print_header "إعداد السجلات"
mkdir -p /var/log/osaric
chown osaric:www-data /var/log/osaric

cat > /etc/logrotate.d/osaric << EOF
/var/log/osaric/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 osaric www-data
    postrotate
        systemctl reload osaric_accounts
    endscript
}
EOF

# 17. إعداد Fail2Ban
print_header "إعداد Fail2Ban"
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# 18. التحقق النهائي
print_header "التحقق من التثبيت"
sleep 5

if systemctl is-active --quiet osaric_accounts; then
    print_status "✅ خدمة التطبيق تعمل بنجاح"
else
    print_error "❌ خطأ في خدمة التطبيق"
fi

if systemctl is-active --quiet nginx; then
    print_status "✅ خدمة Nginx تعمل بنجاح"
else
    print_error "❌ خطأ في خدمة Nginx"
fi

if systemctl is-active --quiet postgresql; then
    print_status "✅ خدمة PostgreSQL تعمل بنجاح"
else
    print_error "❌ خطأ في خدمة PostgreSQL"
fi

print_header "اكتمل التثبيت بنجاح!"
echo -e "${GREEN}🎉 تم تثبيت نظام حسابات أوساريك بنجاح!${NC}"
echo -e "${BLUE}🌐 الموقع: https://$DOMAIN_NAME${NC}"
echo -e "${BLUE}👤 المستخدم الإداري: admin${NC}"
echo -e "${BLUE}🔑 كلمة المرور: admin123${NC}"
echo -e "${YELLOW}⚠️  تأكد من تغيير كلمة المرور الافتراضية!${NC}"
echo -e "${GREEN}📚 الوثائق: https://docs.osaric.com${NC}"
