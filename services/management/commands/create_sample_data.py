from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from services.models import SystemSettings, LicenseInfo, TaskbarSettings
import json


class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية للخدمات'

    def handle(self, *args, **options):
        self.stdout.write('إنشاء بيانات تجريبية للخدمات...')

        # إنشاء إعدادات النظام
        settings_data = [
            {
                'key': 'company_name',
                'value': 'شركة أوساريك للحسابات',
                'category': 'عام',
                'description': 'اسم الشركة',
                'value_type': 'STRING'
            },
            {
                'key': 'max_users',
                'value': '10',
                'category': 'المستخدمين',
                'description': 'الحد الأقصى للمستخدمين',
                'value_type': 'INTEGER'
            },
            {
                'key': 'backup_auto',
                'value': 'true',
                'category': 'النسخ الاحتياطي',
                'description': 'النسخ الاحتياطي التلقائي',
                'value_type': 'BOOLEAN'
            },
            {
                'key': 'invoice_auto_number',
                'value': 'true',
                'category': 'الفواتير',
                'description': 'ترقيم الفواتير تلقائياً',
                'value_type': 'BOOLEAN'
            },
            {
                'key': 'default_currency',
                'value': 'SAR',
                'category': 'المالية',
                'description': 'العملة الافتراضية',
                'value_type': 'STRING'
            },
            {
                'key': 'tax_rate',
                'value': '15.0',
                'category': 'المالية',
                'description': 'معدل الضريبة الافتراضي',
                'value_type': 'FLOAT'
            },
            {
                'key': 'warehouse_tracking',
                'value': 'true',
                'category': 'المخازن',
                'description': 'تتبع المخزون',
                'value_type': 'BOOLEAN'
            },
            {
                'key': 'cost_method',
                'value': 'FIFO',
                'category': 'المخازن',
                'description': 'طريقة حساب التكلفة',
                'value_type': 'STRING'
            },
            {
                'key': 'print_template',
                'value': 'default',
                'category': 'الطباعة',
                'description': 'قالب الطباعة الافتراضي',
                'value_type': 'STRING'
            },
            {
                'key': 'barcode_type',
                'value': 'CODE128',
                'category': 'الباركود',
                'description': 'نوع الباركود الافتراضي',
                'value_type': 'STRING'
            },
            {
                'key': 'system_notifications',
                'value': '{"email": true, "sms": false, "push": true}',
                'category': 'الإشعارات',
                'description': 'إعدادات الإشعارات',
                'value_type': 'JSON'
            },
            {
                'key': 'session_timeout',
                'value': '30',
                'category': 'الأمان',
                'description': 'مهلة انتهاء الجلسة (بالدقائق)',
                'value_type': 'INTEGER'
            },
            {
                'key': 'decimal_places',
                'value': '2',
                'category': 'المالية',
                'description': 'عدد الخانات العشرية',
                'value_type': 'INTEGER'
            },
        ]

        for setting_data in settings_data:
            setting, created = SystemSettings.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
            if created:
                self.stdout.write(f'تم إنشاء إعداد: {setting.key}')

        # إنشاء معلومات ترخيص تجريبية
        if not LicenseInfo.objects.exists():
            license_info = LicenseInfo.objects.create(
                license_key='TRIAL-2024-OSARIC-DEMO',
                license_type='TRIAL',
                customer_name='عميل تجريبي',
                customer_email='demo@osaric.com',
                company_name='شركة أوساريك للحسابات',
                issued_date=timezone.now(),
                expiry_date=timezone.now() + timedelta(days=30),
                activation_date=timezone.now(),
                max_users=5,
                max_branches=2,
                max_transactions=1000,
                is_active=True,
                is_trial=True,
                features={
                    'sales': True,
                    'purchases': True,
                    'inventory': True,
                    'accounting': True,
                    'reports': True,
                    'branches': False,
                    'advanced_reports': False
                },
                notes='نسخة تجريبية لمدة 30 يوم'
            )
            self.stdout.write(f'تم إنشاء ترخيص تجريبي: {license_info.license_key}')

        # إنشاء إعدادات شريط المهام للمستخدم الأول
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                taskbar_settings, created = TaskbarSettings.objects.get_or_create(
                    user=admin_user,
                    defaults={
                        'position': 'HORIZONTAL',
                        'auto_hide': False,
                        'show_icons': True,
                        'show_text': True,
                        'theme': 'default',
                        'size': 'medium',
                        'menu_order': [
                            'dashboard',
                            'definitions',
                            'sales',
                            'purchases',
                            'inventory',
                            'accounting',
                            'branches',
                            'services',
                            'reports'
                        ],
                        'pinned_items': ['dashboard', 'sales', 'purchases']
                    }
                )
                if created:
                    self.stdout.write(f'تم إنشاء إعدادات شريط المهام للمستخدم: {admin_user.username}')
        except Exception as e:
            self.stdout.write(f'خطأ في إنشاء إعدادات شريط المهام: {e}')

        self.stdout.write(
            self.style.SUCCESS('تم إنشاء البيانات التجريبية للخدمات بنجاح!')
        )
