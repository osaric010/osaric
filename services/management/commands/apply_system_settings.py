from django.core.management.base import BaseCommand
from django.conf import settings
from services.models import SystemSettings
from datetime import datetime


class Command(BaseCommand):
    help = 'تطبيق الإعدادات الافتراضية للنظام'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='فرض إعادة إنشاء الإعدادات الموجودة',
        )
        parser.add_argument(
            '--category',
            type=str,
            help='تطبيق إعدادات فئة معينة فقط',
        )

    def handle(self, *args, **options):
        force = options['force']
        category_filter = options['category']
        
        self.stdout.write(
            self.style.SUCCESS('بدء تطبيق الإعدادات الافتراضية...')
        )
        
        # الإعدادات الافتراضية
        default_settings = self.get_default_settings()
        
        created_count = 0
        updated_count = 0
        
        for setting_data in default_settings:
            # تطبيق فلتر الفئة إذا تم تحديده
            if category_filter and setting_data['category'] != category_filter:
                continue
            
            setting, created = SystemSettings.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    f"✓ تم إنشاء الإعداد: {setting_data['key']}"
                )
            elif force:
                # تحديث الإعداد الموجود
                for field, value in setting_data.items():
                    if field != 'key':
                        setattr(setting, field, value)
                setting.save()
                updated_count += 1
                self.stdout.write(
                    f"↻ تم تحديث الإعداد: {setting_data['key']}"
                )
            else:
                self.stdout.write(
                    f"- الإعداد موجود: {setting_data['key']}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nتم الانتهاء! تم إنشاء {created_count} إعداد وتحديث {updated_count} إعداد.'
            )
        )

    def get_default_settings(self):
        """إرجاع الإعدادات الافتراضية"""
        return [
            # إعدادات الشركة
            {
                'key': 'company_name',
                'value': 'شركة أوساريك للحسابات',
                'description': 'اسم الشركة',
                'category': 'معلومات الشركة',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'company_address',
                'value': 'الرياض، المملكة العربية السعودية',
                'description': 'عنوان الشركة',
                'category': 'معلومات الشركة',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'company_phone',
                'value': '+966501234567',
                'description': 'هاتف الشركة',
                'category': 'معلومات الشركة',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'company_email',
                'value': 'info@osaric.com',
                'description': 'بريد الشركة الإلكتروني',
                'category': 'معلومات الشركة',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'tax_number',
                'value': '123456789012345',
                'description': 'الرقم الضريبي للشركة',
                'category': 'معلومات الشركة',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'company_logo',
                'value': '',
                'description': 'شعار الشركة',
                'category': 'معلومات الشركة',
                'value_type': 'FILE',
                'is_editable': True,
            },
            
            # الإعدادات المالية
            {
                'key': 'default_currency',
                'value': 'EGP',
                'description': 'العملة الافتراضية',
                'category': 'الإعدادات المالية',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'currency_symbol',
                'value': 'ج.م',
                'description': 'رمز العملة',
                'category': 'الإعدادات المالية',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'decimal_places',
                'value': '2',
                'description': 'عدد الخانات العشرية',
                'category': 'الإعدادات المالية',
                'value_type': 'INTEGER',
                'is_editable': True,
            },
            {
                'key': 'tax_rate',
                'value': '14.0',
                'description': 'معدل ضريبة القيمة المضافة (%)',
                'category': 'الإعدادات المالية',
                'value_type': 'FLOAT',
                'is_editable': True,
            },
            {
                'key': 'fiscal_year_start',
                'value': '01-01',
                'description': 'بداية السنة المالية (شهر-يوم)',
                'category': 'الإعدادات المالية',
                'value_type': 'STRING',
                'is_editable': True,
            },
            
            # إعدادات النظام
            {
                'key': 'system_language',
                'value': 'ar',
                'description': 'لغة النظام',
                'category': 'إعدادات النظام',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'timezone',
                'value': 'Asia/Riyadh',
                'description': 'المنطقة الزمنية',
                'category': 'إعدادات النظام',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'session_timeout',
                'value': '30',
                'description': 'مهلة انتهاء الجلسة (دقيقة)',
                'category': 'إعدادات النظام',
                'value_type': 'INTEGER',
                'is_editable': True,
            },
            {
                'key': 'max_users',
                'value': '50',
                'description': 'الحد الأقصى للمستخدمين',
                'category': 'إعدادات النظام',
                'value_type': 'INTEGER',
                'is_editable': True,
            },
            {
                'key': 'system_version',
                'value': '1.0.0',
                'description': 'إصدار النظام',
                'category': 'إعدادات النظام',
                'value_type': 'STRING',
                'is_editable': False,
            },
            {
                'key': 'system_install_date',
                'value': datetime.now().strftime('%Y-%m-%d'),
                'description': 'تاريخ تثبيت النظام',
                'category': 'إعدادات النظام',
                'value_type': 'STRING',
                'is_editable': False,
            },
            
            # إعدادات الأمان
            {
                'key': 'password_min_length',
                'value': '8',
                'description': 'الحد الأدنى لطول كلمة المرور',
                'category': 'إعدادات الأمان',
                'value_type': 'INTEGER',
                'is_editable': True,
            },
            {
                'key': 'password_require_uppercase',
                'value': 'true',
                'description': 'يتطلب أحرف كبيرة في كلمة المرور',
                'category': 'إعدادات الأمان',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
            {
                'key': 'password_require_numbers',
                'value': 'true',
                'description': 'يتطلب أرقام في كلمة المرور',
                'category': 'إعدادات الأمان',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
            {
                'key': 'password_require_symbols',
                'value': 'false',
                'description': 'يتطلب رموز في كلمة المرور',
                'category': 'إعدادات الأمان',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
            
            # إعدادات الطباعة
            {
                'key': 'print_template',
                'value': 'default',
                'description': 'قالب الطباعة الافتراضي',
                'category': 'إعدادات الطباعة',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'print_logo',
                'value': 'true',
                'description': 'طباعة شعار الشركة',
                'category': 'إعدادات الطباعة',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
            {
                'key': 'print_company_info',
                'value': 'true',
                'description': 'طباعة معلومات الشركة',
                'category': 'إعدادات الطباعة',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
            {
                'key': 'print_terms',
                'value': 'true',
                'description': 'طباعة الشروط والأحكام',
                'category': 'إعدادات الطباعة',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
            {
                'key': 'print_signature',
                'value': 'false',
                'description': 'طباعة مكان التوقيع',
                'category': 'إعدادات الطباعة',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
            {
                'key': 'print_copies',
                'value': '1',
                'description': 'عدد النسخ المطبوعة',
                'category': 'إعدادات الطباعة',
                'value_type': 'INTEGER',
                'is_editable': True,
            },
            
            # إعدادات الباركود
            {
                'key': 'barcode_type',
                'value': 'CODE128',
                'description': 'نوع الباركود',
                'category': 'إعدادات الباركود',
                'value_type': 'STRING',
                'is_editable': True,
            },
            {
                'key': 'barcode_width',
                'value': '2',
                'description': 'عرض خطوط الباركود',
                'category': 'إعدادات الباركود',
                'value_type': 'INTEGER',
                'is_editable': True,
            },
            {
                'key': 'barcode_height',
                'value': '50',
                'description': 'ارتفاع الباركود',
                'category': 'إعدادات الباركود',
                'value_type': 'INTEGER',
                'is_editable': True,
            },
            {
                'key': 'barcode_show_text',
                'value': 'true',
                'description': 'إظهار النص تحت الباركود',
                'category': 'إعدادات الباركود',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
            {
                'key': 'enable_barcode',
                'value': 'true',
                'description': 'تفعيل الباركود',
                'category': 'إعدادات الباركود',
                'value_type': 'BOOLEAN',
                'is_editable': True,
            },
        ]
