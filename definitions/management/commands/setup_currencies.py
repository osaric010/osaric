"""
أمر إعداد العملات
Setup currencies management command
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from definitions.models import Currency
from services.models import SystemSettings
from decimal import Decimal


class Command(BaseCommand):
    help = 'إعداد العملات الأساسية وتحديث إعدادات النظام'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-rates',
            action='store_true',
            help='تحديث أسعار الصرف',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='إعادة تعيين جميع العملات',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 بدء إعداد العملات...')
        )

        try:
            with transaction.atomic():
                if options['reset']:
                    self.reset_currencies()
                
                self.setup_base_currency()
                self.setup_other_currencies()
                self.setup_currency_settings()
                
                if options['update_rates']:
                    self.update_exchange_rates()
                
                self.update_existing_records()

            self.stdout.write(
                self.style.SUCCESS('✅ تم إعداد العملات بنجاح!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ خطأ في إعداد العملات: {e}')
            )

    def reset_currencies(self):
        """إعادة تعيين جميع العملات"""
        self.stdout.write('🔄 إعادة تعيين العملات...')
        Currency.objects.all().delete()

    def setup_base_currency(self):
        """إعداد العملة الأساسية (الجنيه المصري)"""
        self.stdout.write('💰 إعداد العملة الأساسية...')
        
        # إلغاء تفعيل جميع العملات الأساسية الأخرى
        Currency.objects.filter(is_base_currency=True).update(is_base_currency=False)
        
        # إنشاء أو تحديث الجنيه المصري
        currency, created = Currency.objects.get_or_create(
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
            currency.name = 'الجنيه المصري'
            currency.symbol = 'ج.م'
            currency.exchange_rate = Decimal('1.0000')
            currency.is_base_currency = True
            currency.is_active = True
            currency.save()
            
        action = "تم إنشاء" if created else "تم تحديث"
        self.stdout.write(f'  ✅ {action} العملة الأساسية: {currency.name}')

    def setup_other_currencies(self):
        """إعداد العملات الأخرى"""
        self.stdout.write('🌍 إعداد العملات الأخرى...')
        
        other_currencies = [
            {
                'code': 'USD',
                'name': 'الدولار الأمريكي',
                'symbol': '$',
                'exchange_rate': Decimal('30.90'),
            },
            {
                'code': 'EUR',
                'name': 'اليورو',
                'symbol': '€',
                'exchange_rate': Decimal('33.50'),
            },
            {
                'code': 'SAR',
                'name': 'الريال السعودي',
                'symbol': 'ر.س',
                'exchange_rate': Decimal('8.24'),
            },
            {
                'code': 'AED',
                'name': 'الدرهم الإماراتي',
                'symbol': 'د.إ',
                'exchange_rate': Decimal('8.41'),
            },
            {
                'code': 'GBP',
                'name': 'الجنيه الإسترليني',
                'symbol': '£',
                'exchange_rate': Decimal('39.20'),
            },
            {
                'code': 'KWD',
                'name': 'الدينار الكويتي',
                'symbol': 'د.ك',
                'exchange_rate': Decimal('100.50'),
            },
            {
                'code': 'QAR',
                'name': 'الريال القطري',
                'symbol': 'ر.ق',
                'exchange_rate': Decimal('8.48'),
            },
            {
                'code': 'BHD',
                'name': 'الدينار البحريني',
                'symbol': 'د.ب',
                'exchange_rate': Decimal('81.90'),
            },
            {
                'code': 'OMR',
                'name': 'الريال العماني',
                'symbol': 'ر.ع',
                'exchange_rate': Decimal('80.25'),
            },
            {
                'code': 'JOD',
                'name': 'الدينار الأردني',
                'symbol': 'د.أ',
                'exchange_rate': Decimal('43.60'),
            }
        ]

        created_count = 0
        for curr_data in other_currencies:
            curr_data['is_base_currency'] = False
            curr_data['is_active'] = True
            
            currency, created = Currency.objects.get_or_create(
                code=curr_data['code'],
                defaults=curr_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✅ تم إنشاء: {currency.name} ({currency.code})')
            else:
                # تحديث البيانات الموجودة
                for key, value in curr_data.items():
                    if key != 'code':
                        setattr(currency, key, value)
                currency.save()
                self.stdout.write(f'  ↻ تم تحديث: {currency.name} ({currency.code})')

        self.stdout.write(f'  📊 إجمالي العملات المنشأة: {created_count}')

    def setup_currency_settings(self):
        """إعداد إعدادات العملة في النظام"""
        self.stdout.write('⚙️ إعداد إعدادات العملة...')
        
        currency_settings = [
            ('default_currency', 'EGP', 'العملة الافتراضية', 'الإعدادات المالية', 'STRING'),
            ('currency_symbol', 'ج.م', 'رمز العملة', 'الإعدادات المالية', 'STRING'),
            ('currency_name', 'الجنيه المصري', 'اسم العملة', 'الإعدادات المالية', 'STRING'),
            ('decimal_places', '2', 'عدد الخانات العشرية', 'الإعدادات المالية', 'INTEGER'),
            ('currency_position', 'after', 'موضع رمز العملة', 'الإعدادات المالية', 'STRING'),
            ('thousands_separator', ',', 'فاصل الآلاف', 'الإعدادات المالية', 'STRING'),
            ('decimal_separator', '.', 'فاصل العشرية', 'الإعدادات المالية', 'STRING'),
            ('show_currency_code', 'false', 'إظهار كود العملة', 'الإعدادات المالية', 'BOOLEAN'),
            ('auto_update_rates', 'false', 'تحديث أسعار الصرف تلقائياً', 'الإعدادات المالية', 'BOOLEAN'),
        ]

        updated_count = 0
        for key, value, description, category, value_type in currency_settings:
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
            
            if not created:
                setting.value = value
                setting.save()
                updated_count += 1

            action = "تم إنشاء" if created else "تم تحديث"
            self.stdout.write(f'  ✅ {action} إعداد: {description}')

    def update_exchange_rates(self):
        """تحديث أسعار الصرف (يمكن ربطها بـ API خارجي لاحقاً)"""
        self.stdout.write('📈 تحديث أسعار الصرف...')
        
        # هنا يمكن إضافة كود لجلب أسعار الصرف من API خارجي
        # مثل: https://api.exchangerate-api.com/v4/latest/EGP
        
        self.stdout.write('  ℹ️ أسعار الصرف ثابتة حالياً (يمكن تحديثها لاحقاً)')

    def update_existing_records(self):
        """تحديث السجلات الموجودة لتستخدم العملة الافتراضية"""
        self.stdout.write('🔄 تحديث السجلات الموجودة...')
        
        try:
            egp_currency = Currency.objects.get(code='EGP', is_base_currency=True)
            
            # تحديث الأشخاص والجهات
            from definitions.models import Person, Bank, Treasury
            persons_updated = Person.objects.filter(currency__isnull=True).update(currency=egp_currency)
            banks_updated = Bank.objects.filter(currency__isnull=True).update(currency=egp_currency)
            treasuries_updated = Treasury.objects.filter(currency__isnull=True).update(currency=egp_currency)
            
            # تحديث فواتير المبيعات والمشتريات
            try:
                from sales.models import SalesInvoice, PriceList, Quotation
                sales_updated = SalesInvoice.objects.filter(currency__isnull=True).update(
                    currency=egp_currency, exchange_rate=Decimal('1.0')
                )
                pricelists_updated = PriceList.objects.filter(currency__isnull=True).update(currency=egp_currency)
                quotations_updated = Quotation.objects.filter(currency__isnull=True).update(
                    currency=egp_currency, exchange_rate=Decimal('1.0')
                )
            except:
                sales_updated = pricelists_updated = quotations_updated = 0
            
            try:
                from purchases.models import PurchaseInvoice
                purchases_updated = PurchaseInvoice.objects.filter(currency__isnull=True).update(
                    currency=egp_currency, exchange_rate=Decimal('1.0')
                )
            except:
                purchases_updated = 0

            self.stdout.write(f'  ✅ تم تحديث {persons_updated} شخص/جهة')
            self.stdout.write(f'  ✅ تم تحديث {banks_updated} بنك')
            self.stdout.write(f'  ✅ تم تحديث {treasuries_updated} خزينة')
            self.stdout.write(f'  ✅ تم تحديث {sales_updated} فاتورة مبيعات')
            self.stdout.write(f'  ✅ تم تحديث {pricelists_updated} قائمة أسعار')
            self.stdout.write(f'  ✅ تم تحديث {quotations_updated} عرض سعر')
            self.stdout.write(f'  ✅ تم تحديث {purchases_updated} فاتورة مشتريات')

        except Currency.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ لم يتم العثور على الجنيه المصري')
            )

    def display_summary(self):
        """عرض ملخص العملات"""
        self.stdout.write('\n📋 ملخص العملات:')
        self.stdout.write('-' * 50)
        
        for currency in Currency.objects.all().order_by('name'):
            status = "🏆 أساسية" if currency.is_base_currency else "💱 فرعية"
            active = "✅ نشطة" if currency.is_active else "❌ غير نشطة"
            
            self.stdout.write(
                f'{status} {currency.name} ({currency.code}) - {currency.symbol} - '
                f'سعر الصرف: {currency.exchange_rate} - {active}'
            )
        
        total_currencies = Currency.objects.count()
        active_currencies = Currency.objects.filter(is_active=True).count()
        
        self.stdout.write(f'\n📊 إجمالي العملات: {total_currencies}')
        self.stdout.write(f'📊 العملات النشطة: {active_currencies}')
        
        base_currency = Currency.objects.filter(is_base_currency=True).first()
        if base_currency:
            self.stdout.write(f'🏆 العملة الأساسية: {base_currency.name} ({base_currency.symbol})')
