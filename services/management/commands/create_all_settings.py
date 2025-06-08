from django.core.management.base import BaseCommand
from services.models import SystemSettings


class Command(BaseCommand):
    help = 'إنشاء جميع إعدادات النظام الشاملة'

    def handle(self, *args, **options):
        self.stdout.write('إنشاء جميع إعدادات النظام...')

        # جميع إعدادات النظام الشاملة
        all_settings = [
            # إعدادات عامة
            {
                'key': 'company_name',
                'value': 'شركة أوساريك للحسابات',
                'category': 'عام',
                'description': 'اسم الشركة',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'company_address',
                'value': 'الرياض، المملكة العربية السعودية',
                'category': 'عام',
                'description': 'عنوان الشركة',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'company_phone',
                'value': '+966501234567',
                'category': 'عام',
                'description': 'هاتف الشركة',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'company_email',
                'value': 'info@osaric.com',
                'category': 'عام',
                'description': 'بريد الشركة الإلكتروني',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'company_logo',
                'value': '/static/images/logo.png',
                'category': 'عام',
                'description': 'شعار الشركة',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'system_language',
                'value': 'ar',
                'category': 'عام',
                'description': 'لغة النظام الافتراضية',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'timezone',
                'value': 'Asia/Riyadh',
                'category': 'عام',
                'description': 'المنطقة الزمنية',
                'value_type': 'STRING',
                'is_editable': True
            },

            # إعدادات المستخدمين والأمان
            {
                'key': 'max_users',
                'value': '50',
                'category': 'المستخدمين',
                'description': 'الحد الأقصى للمستخدمين',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'password_min_length',
                'value': '8',
                'category': 'المستخدمين',
                'description': 'الحد الأدنى لطول كلمة المرور',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'password_require_uppercase',
                'value': 'true',
                'category': 'المستخدمين',
                'description': 'يتطلب أحرف كبيرة في كلمة المرور',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'password_require_numbers',
                'value': 'true',
                'category': 'المستخدمين',
                'description': 'يتطلب أرقام في كلمة المرور',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'password_require_symbols',
                'value': 'false',
                'category': 'المستخدمين',
                'description': 'يتطلب رموز خاصة في كلمة المرور',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'session_timeout',
                'value': '30',
                'category': 'المستخدمين',
                'description': 'مهلة انتهاء الجلسة (بالدقائق)',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'max_login_attempts',
                'value': '5',
                'category': 'المستخدمين',
                'description': 'عدد محاولات تسجيل الدخول المسموحة',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'lockout_duration',
                'value': '15',
                'category': 'المستخدمين',
                'description': 'مدة الحظر بعد المحاولات الفاشلة (بالدقائق)',
                'value_type': 'INTEGER',
                'is_editable': True
            },

            # إعدادات المالية والمحاسبة
            {
                'key': 'default_currency',
                'value': 'EGP',
                'category': 'المالية',
                'description': 'العملة الافتراضية',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'currency_symbol',
                'value': 'ج.م',
                'category': 'المالية',
                'description': 'رمز العملة',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'decimal_places',
                'value': '2',
                'category': 'المالية',
                'description': 'عدد الخانات العشرية',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'tax_rate',
                'value': '14.0',
                'category': 'المالية',
                'description': 'معدل الضريبة الافتراضي (%)',
                'value_type': 'FLOAT',
                'is_editable': True
            },
            {
                'key': 'tax_number',
                'value': '123456789012345',
                'category': 'المالية',
                'description': 'الرقم الضريبي للشركة',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'fiscal_year_start',
                'value': '01-01',
                'category': 'المالية',
                'description': 'بداية السنة المالية (شهر-يوم)',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'enable_multi_currency',
                'value': 'false',
                'category': 'المالية',
                'description': 'تفعيل العملات المتعددة',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'auto_exchange_rates',
                'value': 'false',
                'category': 'المالية',
                'description': 'تحديث أسعار الصرف تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },

            # إعدادات المبيعات
            {
                'key': 'sales_auto_numbering',
                'value': 'true',
                'category': 'المبيعات',
                'description': 'ترقيم فواتير المبيعات تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'sales_number_prefix',
                'value': 'INV',
                'category': 'المبيعات',
                'description': 'بادئة رقم فاتورة المبيعات',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'sales_number_length',
                'value': '6',
                'category': 'المبيعات',
                'description': 'طول رقم فاتورة المبيعات',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'sales_default_payment_terms',
                'value': '30',
                'category': 'المبيعات',
                'description': 'شروط الدفع الافتراضية (بالأيام)',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'sales_allow_negative_stock',
                'value': 'false',
                'category': 'المبيعات',
                'description': 'السماح بالبيع من مخزون سالب',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'sales_require_customer',
                'value': 'true',
                'category': 'المبيعات',
                'description': 'يتطلب تحديد عميل في الفاتورة',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'sales_auto_discount',
                'value': 'false',
                'category': 'المبيعات',
                'description': 'تطبيق الخصومات تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'sales_commission_rate',
                'value': '5.0',
                'category': 'المبيعات',
                'description': 'معدل العمولة الافتراضي (%)',
                'value_type': 'FLOAT',
                'is_editable': True
            },

            # إعدادات المشتريات
            {
                'key': 'purchase_auto_numbering',
                'value': 'true',
                'category': 'المشتريات',
                'description': 'ترقيم فواتير المشتريات تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'purchase_number_prefix',
                'value': 'PUR',
                'category': 'المشتريات',
                'description': 'بادئة رقم فاتورة المشتريات',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'purchase_number_length',
                'value': '6',
                'category': 'المشتريات',
                'description': 'طول رقم فاتورة المشتريات',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'purchase_default_payment_terms',
                'value': '30',
                'category': 'المشتريات',
                'description': 'شروط الدفع الافتراضية (بالأيام)',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'purchase_require_approval',
                'value': 'false',
                'category': 'المشتريات',
                'description': 'يتطلب موافقة على فواتير المشتريات',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'purchase_approval_limit',
                'value': '10000.0',
                'category': 'المشتريات',
                'description': 'حد الموافقة على المشتريات',
                'value_type': 'FLOAT',
                'is_editable': True
            },
            {
                'key': 'purchase_auto_receive',
                'value': 'true',
                'category': 'المشتريات',
                'description': 'استلام المشتريات تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },

            # إعدادات المخازن والمخزون
            {
                'key': 'inventory_tracking_method',
                'value': 'FIFO',
                'category': 'المخازن',
                'description': 'طريقة تتبع المخزون',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'inventory_auto_reorder',
                'value': 'false',
                'category': 'المخازن',
                'description': 'إعادة الطلب التلقائي',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'inventory_low_stock_alert',
                'value': 'true',
                'category': 'المخازن',
                'description': 'تنبيه المخزون المنخفض',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'inventory_negative_stock',
                'value': 'false',
                'category': 'المخازن',
                'description': 'السماح بالمخزون السالب',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'inventory_batch_tracking',
                'value': 'false',
                'category': 'المخازن',
                'description': 'تتبع الدفعات',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'inventory_serial_tracking',
                'value': 'false',
                'category': 'المخازن',
                'description': 'تتبع الأرقام التسلسلية',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'inventory_expiry_tracking',
                'value': 'false',
                'category': 'المخازن',
                'description': 'تتبع تواريخ الانتهاء',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },

            # إعدادات الأصناف
            {
                'key': 'item_auto_code',
                'value': 'true',
                'category': 'الأصناف',
                'description': 'ترميز الأصناف تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'item_code_prefix',
                'value': 'ITM',
                'category': 'الأصناف',
                'description': 'بادئة رمز الصنف',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'item_code_length',
                'value': '8',
                'category': 'الأصناف',
                'description': 'طول رمز الصنف',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'item_require_barcode',
                'value': 'false',
                'category': 'الأصناف',
                'description': 'يتطلب باركود للصنف',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'item_auto_barcode',
                'value': 'true',
                'category': 'الأصناف',
                'description': 'إنشاء باركود تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'item_multiple_units',
                'value': 'true',
                'category': 'الأصناف',
                'description': 'وحدات قياس متعددة للصنف',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },

            # إعدادات الباركود
            {
                'key': 'barcode_type',
                'value': 'CODE128',
                'category': 'الباركود',
                'description': 'نوع الباركود الافتراضي',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'barcode_width',
                'value': '2',
                'category': 'الباركود',
                'description': 'عرض الباركود',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'barcode_height',
                'value': '50',
                'category': 'الباركود',
                'description': 'ارتفاع الباركود',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'barcode_show_text',
                'value': 'true',
                'category': 'الباركود',
                'description': 'إظهار النص تحت الباركود',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },

            # إعدادات الطباعة
            {
                'key': 'print_template',
                'value': 'default',
                'category': 'الطباعة',
                'description': 'قالب الطباعة الافتراضي',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'print_logo',
                'value': 'true',
                'category': 'الطباعة',
                'description': 'طباعة شعار الشركة',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'print_company_info',
                'value': 'true',
                'category': 'الطباعة',
                'description': 'طباعة معلومات الشركة',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'print_terms',
                'value': 'true',
                'category': 'الطباعة',
                'description': 'طباعة الشروط والأحكام',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'print_signature',
                'value': 'false',
                'category': 'الطباعة',
                'description': 'طباعة مكان التوقيع',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'print_copies',
                'value': '1',
                'category': 'الطباعة',
                'description': 'عدد النسخ المطبوعة',
                'value_type': 'INTEGER',
                'is_editable': True
            },

            # إعدادات التقارير
            {
                'key': 'report_date_format',
                'value': 'Y-m-d',
                'category': 'التقارير',
                'description': 'تنسيق التاريخ في التقارير',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'report_auto_refresh',
                'value': 'false',
                'category': 'التقارير',
                'description': 'تحديث التقارير تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'report_export_format',
                'value': 'PDF',
                'category': 'التقارير',
                'description': 'تنسيق تصدير التقارير الافتراضي',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'report_max_records',
                'value': '10000',
                'category': 'التقارير',
                'description': 'الحد الأقصى للسجلات في التقرير',
                'value_type': 'INTEGER',
                'is_editable': True
            },

            # إعدادات النسخ الاحتياطي
            {
                'key': 'backup_auto',
                'value': 'false',
                'category': 'النسخ الاحتياطي',
                'description': 'النسخ الاحتياطي التلقائي',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'backup_frequency',
                'value': 'daily',
                'category': 'النسخ الاحتياطي',
                'description': 'تكرار النسخ الاحتياطي',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'backup_time',
                'value': '02:00',
                'category': 'النسخ الاحتياطي',
                'description': 'وقت النسخ الاحتياطي',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'backup_retention_days',
                'value': '30',
                'category': 'النسخ الاحتياطي',
                'description': 'مدة الاحتفاظ بالنسخ (بالأيام)',
                'value_type': 'INTEGER',
                'is_editable': True
            },

            # إعدادات الإشعارات
            {
                'key': 'notifications_email',
                'value': 'true',
                'category': 'الإشعارات',
                'description': 'إشعارات البريد الإلكتروني',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'notifications_sms',
                'value': 'false',
                'category': 'الإشعارات',
                'description': 'إشعارات الرسائل النصية',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'notifications_system',
                'value': 'true',
                'category': 'الإشعارات',
                'description': 'إشعارات النظام',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'email_smtp_server',
                'value': 'smtp.gmail.com',
                'category': 'الإشعارات',
                'description': 'خادم البريد الإلكتروني',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'email_smtp_port',
                'value': '587',
                'category': 'الإشعارات',
                'description': 'منفذ خادم البريد',
                'value_type': 'INTEGER',
                'is_editable': True
            },

            # إعدادات الفروع
            {
                'key': 'enable_branches',
                'value': 'false',
                'category': 'الفروع',
                'description': 'تفعيل نظام الفروع',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'branch_auto_code',
                'value': 'true',
                'category': 'الفروع',
                'description': 'ترميز الفروع تلقائياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'branch_separate_accounting',
                'value': 'false',
                'category': 'الفروع',
                'description': 'محاسبة منفصلة للفروع',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'branch_inventory_sync',
                'value': 'true',
                'category': 'الفروع',
                'description': 'مزامنة المخزون بين الفروع',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },

            # إعدادات واجهة المستخدم
            {
                'key': 'ui_theme',
                'value': 'default',
                'category': 'واجهة المستخدم',
                'description': 'مظهر الواجهة',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_sidebar_collapsed',
                'value': 'false',
                'category': 'واجهة المستخدم',
                'description': 'طي الشريط الجانبي افتراضياً',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_show_tooltips',
                'value': 'true',
                'category': 'واجهة المستخدم',
                'description': 'إظهار التلميحات',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_animation_speed',
                'value': 'normal',
                'category': 'واجهة المستخدم',
                'description': 'سرعة الحركات',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_records_per_page',
                'value': '25',
                'category': 'واجهة المستخدم',
                'description': 'عدد السجلات في الصفحة',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'ui_primary_color',
                'value': '#0d6efd',
                'category': 'واجهة المستخدم',
                'description': 'اللون الأساسي',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_secondary_color',
                'value': '#6c757d',
                'category': 'واجهة المستخدم',
                'description': 'اللون الثانوي',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_success_color',
                'value': '#198754',
                'category': 'واجهة المستخدم',
                'description': 'لون النجاح',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_danger_color',
                'value': '#dc3545',
                'category': 'واجهة المستخدم',
                'description': 'لون الخطر',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_warning_color',
                'value': '#ffc107',
                'category': 'واجهة المستخدم',
                'description': 'لون التحذير',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_info_color',
                'value': '#0dcaf0',
                'category': 'واجهة المستخدم',
                'description': 'لون المعلومات',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_font_family',
                'value': 'Cairo, sans-serif',
                'category': 'واجهة المستخدم',
                'description': 'نوع الخط',
                'value_type': 'STRING',
                'is_editable': True
            },
            {
                'key': 'ui_font_size',
                'value': '14',
                'category': 'واجهة المستخدم',
                'description': 'حجم الخط (px)',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'ui_border_radius',
                'value': '8',
                'category': 'واجهة المستخدم',
                'description': 'انحناء الحواف (px)',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'ui_sidebar_width',
                'value': '280',
                'category': 'واجهة المستخدم',
                'description': 'عرض الشريط الجانبي (px)',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'ui_header_height',
                'value': '60',
                'category': 'واجهة المستخدم',
                'description': 'ارتفاع الرأس (px)',
                'value_type': 'INTEGER',
                'is_editable': True
            },
            {
                'key': 'ui_enable_dark_mode',
                'value': 'false',
                'category': 'واجهة المستخدم',
                'description': 'تفعيل الوضع الليلي',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_enable_rtl',
                'value': 'true',
                'category': 'واجهة المستخدم',
                'description': 'تفعيل الاتجاه من اليمين لليسار',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_enable_animations',
                'value': 'true',
                'category': 'واجهة المستخدم',
                'description': 'تفعيل الحركات والانتقالات',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_enable_breadcrumbs',
                'value': 'true',
                'category': 'واجهة المستخدم',
                'description': 'إظهار مسار التنقل',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_enable_notifications',
                'value': 'true',
                'category': 'واجهة المستخدم',
                'description': 'تفعيل الإشعارات',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_table_striped',
                'value': 'true',
                'category': 'واجهة المستخدم',
                'description': 'جداول مخططة',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_table_hover',
                'value': 'true',
                'category': 'واجهة المستخدم',
                'description': 'تأثير التمرير على الجداول',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },
            {
                'key': 'ui_compact_mode',
                'value': 'false',
                'category': 'واجهة المستخدم',
                'description': 'الوضع المضغوط',
                'value_type': 'BOOLEAN',
                'is_editable': True
            },

            # إعدادات النظام (غير قابلة للتعديل)
            {
                'key': 'system_version',
                'value': '1.0.0',
                'category': 'النظام',
                'description': 'إصدار النظام',
                'value_type': 'STRING',
                'is_editable': False
            },
            {
                'key': 'system_install_date',
                'value': '2024-01-01',
                'category': 'النظام',
                'description': 'تاريخ تثبيت النظام',
                'value_type': 'STRING',
                'is_editable': False
            },
            {
                'key': 'database_version',
                'value': '1.0',
                'category': 'النظام',
                'description': 'إصدار قاعدة البيانات',
                'value_type': 'STRING',
                'is_editable': False
            },
        ]

        created_count = 0
        updated_count = 0

        for setting_data in all_settings:
            setting, created = SystemSettings.objects.get_or_create(
                key=setting_data['key'],
                defaults=setting_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'تم إنشاء إعداد: {setting.key}')
            else:
                # تحديث الوصف والفئة إذا تغيرت
                if setting.description != setting_data['description'] or setting.category != setting_data['category']:
                    setting.description = setting_data['description']
                    setting.category = setting_data['category']
                    setting.save()
                    updated_count += 1
                    self.stdout.write(f'تم تحديث إعداد: {setting.key}')

        self.stdout.write(
            self.style.SUCCESS(
                f'تم الانتهاء! تم إنشاء {created_count} إعداد جديد وتحديث {updated_count} إعداد موجود'
            )
        )

        # عرض ملخص الإعدادات حسب الفئة
        categories = {}
        for setting in SystemSettings.objects.all():
            if setting.category not in categories:
                categories[setting.category] = 0
            categories[setting.category] += 1

        self.stdout.write('\nملخص الإعدادات حسب الفئة:')
        for category, count in sorted(categories.items()):
            self.stdout.write(f'- {category}: {count} إعداد')
