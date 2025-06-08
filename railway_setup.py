#!/usr/bin/env python
"""
سكريبت إعداد أولي للنشر على Railway
Initial setup script for Railway deployment
"""

import os
import django
from django.core.management import execute_from_command_line

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osaric_accounts.settings_railway')
django.setup()

def setup_initial_data():
    """إعداد البيانات الأولية"""
    print("🚀 بدء إعداد البيانات الأولية...")
    
    # Import models after Django setup
    from django.contrib.auth.models import User
    from services.models import LicenseInfo, SystemSettings
    from django.utils import timezone
    from datetime import timedelta
    import uuid
    
    try:
        # إنشاء مستخدم إداري إذا لم يكن موجوداً
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@osaric.com',
                password='admin123'
            )
            print("✅ تم إنشاء مستخدم إداري: admin/admin123")
        else:
            admin_user = User.objects.get(username='admin')
            print("✅ المستخدم الإداري موجود")
        
        # إنشاء ترخيص كامل
        if not LicenseInfo.objects.exists():
            license_key = f"RAILWAY-FREE-{str(uuid.uuid4())[:8].upper()}"
            
            license = LicenseInfo.objects.create(
                license_key=license_key,
                license_type='PROFESSIONAL',
                customer_name='مستخدم Railway',
                customer_email='user@railway.app',
                company_name='شركة أوساريك - Railway',
                issued_date=timezone.now(),
                expiry_date=timezone.now() + timedelta(days=365),
                activation_date=timezone.now(),
                max_users=100,
                max_branches=10,
                is_active=True,
                is_trial=False,
                features={
                    'sales': True,
                    'purchases': True,
                    'inventory': True,
                    'accounting': True,
                    'reports': True,
                    'branches': True,
                    'advanced_reports': True,
                    'multi_currency': True,
                    'api_access': True,
                    'backup_restore': True,
                    'data_export': True,
                    'custom_fields': True,
                    'mobile_app': True,
                    'email_notifications': True,
                    'barcode_scanning': True,
                    'custom_reports': True,
                    'advanced_analytics': True
                },
                notes='ترخيص مجاني للنشر على Railway - جميع المميزات مفعلة'
            )
            print(f"✅ تم إنشاء ترخيص: {license_key}")
        else:
            print("✅ الترخيص موجود")
        
        # إنشاء إعدادات النظام الأساسية
        basic_settings = [
            ('company_name', 'شركة أوساريك للحسابات', 'اسم الشركة', 'معلومات الشركة', 'STRING'),
            ('company_address', 'القاهرة، مصر', 'عنوان الشركة', 'معلومات الشركة', 'STRING'),
            ('company_phone', '+20123456789', 'هاتف الشركة', 'معلومات الشركة', 'STRING'),
            ('company_email', 'info@osaric.com', 'بريد الشركة', 'معلومات الشركة', 'STRING'),
            ('default_currency', 'EGP', 'العملة الافتراضية', 'الإعدادات المالية', 'STRING'),
            ('currency_symbol', 'ج.م', 'رمز العملة', 'الإعدادات المالية', 'STRING'),
            ('decimal_places', '2', 'عدد الخانات العشرية', 'الإعدادات المالية', 'INTEGER'),
            ('system_language', 'ar', 'لغة النظام', 'الإعدادات العامة', 'STRING'),
            ('date_format', 'Y-m-d', 'تنسيق التاريخ', 'الإعدادات العامة', 'STRING'),
            ('time_format', 'H:i:s', 'تنسيق الوقت', 'الإعدادات العامة', 'STRING'),
            ('enable_notifications', 'true', 'تفعيل الإشعارات', 'الإعدادات العامة', 'BOOLEAN'),
            ('records_per_page', '25', 'عدد السجلات في الصفحة', 'الإعدادات العامة', 'INTEGER'),
        ]
        
        created_count = 0
        for key, value, description, category, value_type in basic_settings:
            setting, created = SystemSettings.objects.get_or_create(
                key=key,
                defaults={
                    'value': value,
                    'description': description,
                    'category': category,
                    'value_type': value_type,
                    'is_editable': True,
                    'is_system': False
                }
            )
            if created:
                created_count += 1
        
        print(f"✅ تم إنشاء {created_count} إعداد نظام")
        
        print("🎉 تم إعداد البيانات الأولية بنجاح!")
        print("🌐 التطبيق جاهز للاستخدام على Railway!")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في إعداد البيانات: {e}")
        return False

if __name__ == '__main__':
    setup_initial_data()
