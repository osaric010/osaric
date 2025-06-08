"""
Command لتعيين الجنيه المصري كعملة افتراضية في كامل النظام
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from services.models import SystemSettings
from definitions.models import Currency, CompanySettings


class Command(BaseCommand):
    help = 'تعيين الجنيه المصري كعملة افتراضية في كامل النظام'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='فرض التحديث حتى لو كانت الإعدادات موجودة',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(
            self.style.SUCCESS('بدء تعيين الجنيه المصري كعملة افتراضية...')
        )

        try:
            with transaction.atomic():
                # 1. إنشاء/تحديث العملة المصرية
                self.setup_egyptian_currency()
                
                # 2. تحديث إعدادات النظام
                self.update_system_settings(force)
                
                # 3. تحديث إعدادات الشركة
                self.update_company_settings()
                
                # 4. تحديث العملات الأخرى
                self.update_other_currencies()
                
                # 5. عرض ملخص
                self.show_summary()

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'حدث خطأ: {str(e)}')
            )
            raise

        self.stdout.write(
            self.style.SUCCESS('تم تعيين الجنيه المصري كعملة افتراضية بنجاح!')
        )

    def setup_egyptian_currency(self):
        """إنشاء/تحديث العملة المصرية"""
        self.stdout.write('إعداد العملة المصرية...')
        
        egp_currency, created = Currency.objects.get_or_create(
            code='EGP',
            defaults={
                'name': 'الجنيه المصري',
                'symbol': 'ج.م',
                'exchange_rate': Decimal('1.0000'),
                'is_base_currency': True,
                'is_active': True
            }
        )

        if not created:
            # تحديث العملة الموجودة
            egp_currency.name = 'الجنيه المصري'
            egp_currency.symbol = 'ج.م'
            egp_currency.exchange_rate = Decimal('1.0000')
            egp_currency.is_base_currency = True
            egp_currency.is_active = True
            egp_currency.save()
            
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ العملة المصرية: {egp_currency.name} - '
                f'{"تم إنشاؤها" if created else "تم تحديثها"}'
            )
        )
        
        return egp_currency

    def update_system_settings(self, force=False):
        """تحديث إعدادات النظام المالية"""
        self.stdout.write('تحديث إعدادات النظام المالية...')
        
        financial_settings = [
            ('default_currency', 'EGP', 'العملة الافتراضية', 'STRING'),
            ('currency_symbol', 'ج.م', 'رمز العملة', 'STRING'),
            ('currency_name', 'الجنيه المصري', 'اسم العملة', 'STRING'),
            ('decimal_places', '2', 'عدد الخانات العشرية', 'INTEGER'),
            ('tax_rate', '14.0', 'معدل ضريبة القيمة المضافة (%)', 'FLOAT'),
            ('currency_position', 'after', 'موضع رمز العملة', 'STRING'),
            ('thousands_separator', ',', 'فاصل الآلاف', 'STRING'),
            ('decimal_separator', '.', 'فاصل العشرية', 'STRING'),
            ('show_currency_code', 'false', 'إظهار كود العملة', 'BOOLEAN'),
            ('auto_update_rates', 'false', 'تحديث أسعار الصرف تلقائياً', 'BOOLEAN'),
        ]

        updated_count = 0
        created_count = 0

        for key, value, description, value_type in financial_settings:
            setting, created = SystemSettings.objects.get_or_create(
                key=key,
                defaults={
                    'value': value,
                    'description': description,
                    'category': 'الإعدادات المالية',
                    'value_type': value_type,
                    'is_editable': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ تم إنشاء إعداد: {key} = {value}')
            elif force or setting.value != value:
                setting.value = value
                setting.description = description
                setting.value_type = value_type
                setting.save()
                updated_count += 1
                self.stdout.write(f'  ✓ تم تحديث إعداد: {key} = {value}')

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ تم إنشاء {created_count} إعداد وتحديث {updated_count} إعداد'
            )
        )

    def update_company_settings(self):
        """تحديث إعدادات الشركة"""
        self.stdout.write('تحديث إعدادات الشركة...')
        
        try:
            egp_currency = Currency.objects.get(code='EGP')
            company_settings = CompanySettings.get_settings()
            
            if company_settings.default_currency != egp_currency:
                company_settings.default_currency = egp_currency
                company_settings.save()
                self.stdout.write('  ✓ تم تحديث العملة الافتراضية في إعدادات الشركة')
            else:
                self.stdout.write('  ✓ إعدادات الشركة محدثة بالفعل')
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'تحذير: لم يتم تحديث إعدادات الشركة - {str(e)}')
            )

    def update_other_currencies(self):
        """تحديث العملات الأخرى وإلغاء تعيينها كعملة أساسية"""
        self.stdout.write('تحديث العملات الأخرى...')
        
        # إلغاء تعيين العملات الأخرى كعملة أساسية
        updated_count = Currency.objects.exclude(code='EGP').filter(
            is_base_currency=True
        ).update(is_base_currency=False)
        
        if updated_count > 0:
            self.stdout.write(f'  ✓ تم إلغاء تعيين {updated_count} عملة كعملة أساسية')
        
        # تحديث أسعار الصرف للعملات الشائعة (أمثلة)
        exchange_rates = {
            'USD': 30.90,  # دولار أمريكي
            'EUR': 33.50,  # يورو
            'SAR': 8.24,   # ريال سعودي
            'AED': 8.41,   # درهم إماراتي
            'GBP': 39.20,  # جنيه إسترليني
            'KWD': 100.50, # دينار كويتي
            'QAR': 8.49,   # ريال قطري
            'OMR': 80.30,  # ريال عماني
            'BHD': 81.90,  # دينار بحريني
            'JOD': 43.60,  # دينار أردني
        }
        
        updated_rates = 0
        for currency_code, rate in exchange_rates.items():
            try:
                currency = Currency.objects.get(code=currency_code, is_active=True)
                if currency.exchange_rate != Decimal(str(rate)):
                    currency.exchange_rate = Decimal(str(rate))
                    currency.save()
                    updated_rates += 1
                    self.stdout.write(f'  ✓ تم تحديث سعر صرف {currency_code}: {rate}')
            except Currency.DoesNotExist:
                continue
        
        if updated_rates > 0:
            self.stdout.write(f'  ✓ تم تحديث {updated_rates} سعر صرف')

    def show_summary(self):
        """عرض ملخص الإعدادات الحالية"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('ملخص الإعدادات المالية الحالية:'))
        self.stdout.write('='*50)
        
        # العملة الأساسية
        try:
            base_currency = Currency.objects.get(is_base_currency=True)
            self.stdout.write(f'العملة الأساسية: {base_currency.name} ({base_currency.code})')
            self.stdout.write(f'رمز العملة: {base_currency.symbol}')
        except Currency.DoesNotExist:
            self.stdout.write(self.style.ERROR('لا توجد عملة أساسية محددة!'))
        
        # إعدادات النظام
        financial_keys = [
            'default_currency', 'currency_symbol', 'decimal_places', 
            'tax_rate', 'currency_position'
        ]
        
        self.stdout.write('\nإعدادات النظام المالية:')
        for key in financial_keys:
            try:
                setting = SystemSettings.objects.get(key=key)
                self.stdout.write(f'  {setting.description}: {setting.value}')
            except SystemSettings.DoesNotExist:
                self.stdout.write(f'  {key}: غير محدد')
        
        # عدد العملات النشطة
        active_currencies_count = Currency.objects.filter(is_active=True).count()
        self.stdout.write(f'\nعدد العملات النشطة: {active_currencies_count}')
        
        # العملات الأخرى
        other_currencies = Currency.objects.filter(
            is_active=True, 
            is_base_currency=False
        ).order_by('name')[:5]
        
        if other_currencies:
            self.stdout.write('\nبعض العملات الأخرى:')
            for currency in other_currencies:
                self.stdout.write(
                    f'  {currency.name} ({currency.code}): {currency.exchange_rate}'
                )
        
        self.stdout.write('='*50)
