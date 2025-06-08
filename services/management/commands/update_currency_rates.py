"""
Command لتحديث أسعار العملات من البنوك المصرية
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from services.currency_rates import currency_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'تحديث أسعار العملات من البنوك المصرية'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bank',
            type=str,
            help='تحديث بنك معين (cbe, nbe, cib, qnb)',
        )
        parser.add_argument(
            '--currency',
            type=str,
            help='تحديث عملة معينة (USD, EUR, GBP, etc.)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='فرض التحديث حتى لو تم التحديث مؤخراً',
        )

    def handle(self, *args, **options):
        bank = options.get('bank')
        currency = options.get('currency')
        force = options.get('force', False)
        
        self.stdout.write(
            self.style.SUCCESS('بدء تحديث أسعار العملات من البنوك المصرية...')
        )
        
        start_time = timezone.now()
        
        try:
            if bank:
                # تحديث بنك معين
                result = self.update_specific_bank(bank)
            else:
                # تحديث جميع البنوك
                result = currency_service.update_all_rates()
            
            # عرض النتائج
            self.display_results(result, start_time)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'حدث خطأ أثناء التحديث: {str(e)}')
            )
            raise

    def update_specific_bank(self, bank_code):
        """تحديث بنك معين"""
        bank_methods = {
            'cbe': currency_service.get_cbe_rates,
            'nbe': currency_service.get_nbe_rates,
            'cib': currency_service.get_cib_rates,
            'qnb': currency_service.get_qnb_rates,
        }
        
        if bank_code not in bank_methods:
            self.stdout.write(
                self.style.ERROR(f'البنك {bank_code} غير مدعوم. البنوك المتاحة: {", ".join(bank_methods.keys())}')
            )
            return {'success': 0, 'failed': 1, 'banks': []}
        
        bank_names = {
            'cbe': 'البنك المركزي المصري',
            'nbe': 'البنك الأهلي المصري',
            'cib': 'البنك التجاري الدولي',
            'qnb': 'بنك قطر الوطني الأهلي',
        }
        
        bank_name = bank_names[bank_code]
        method = bank_methods[bank_code]
        
        self.stdout.write(f'تحديث أسعار {bank_name}...')
        
        try:
            if method():
                return {
                    'success': 1,
                    'failed': 0,
                    'banks': [{'name': bank_name, 'status': 'success'}]
                }
            else:
                return {
                    'success': 0,
                    'failed': 1,
                    'banks': [{'name': bank_name, 'status': 'failed'}]
                }
        except Exception as e:
            return {
                'success': 0,
                'failed': 1,
                'banks': [{'name': bank_name, 'status': 'error', 'error': str(e)}]
            }

    def display_results(self, result, start_time):
        """عرض نتائج التحديث"""
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('تم الانتهاء من تحديث أسعار العملات'))
        self.stdout.write('='*60)
        
        # إحصائيات عامة
        self.stdout.write(f'البنوك المحدثة بنجاح: {result["success"]}')
        self.stdout.write(f'البنوك الفاشلة: {result["failed"]}')
        self.stdout.write(f'وقت التحديث: {duration:.2f} ثانية')
        
        # تفاصيل كل بنك
        self.stdout.write('\nتفاصيل التحديث:')
        for bank in result['banks']:
            if bank['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ {bank["name"]}: تم التحديث بنجاح')
                )
            elif bank['status'] == 'failed':
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ {bank["name"]}: فشل التحديث')
                )
            elif bank['status'] == 'error':
                self.stdout.write(
                    self.style.ERROR(f'  ✗ {bank["name"]}: خطأ - {bank.get("error", "غير معروف")}')
                )
        
        # عرض أحدث الأسعار
        self.stdout.write('\nأحدث الأسعار:')
        self.display_latest_rates()
        
        self.stdout.write('='*60)

    def display_latest_rates(self):
        """عرض أحدث الأسعار"""
        from definitions.models import EgyptianBankRate
        
        # جلب أحدث الأسعار لكل عملة
        currencies = ['USD', 'EUR', 'GBP', 'SAR', 'AED']
        
        for currency_code in currencies:
            rates = EgyptianBankRate.objects.filter(
                currency__code=currency_code,
                is_active=True
            ).select_related('currency').order_by('-last_updated')[:3]
            
            if rates:
                self.stdout.write(f'\n{currency_code}:')
                for rate in rates:
                    self.stdout.write(
                        f'  {rate.bank_name}: شراء {rate.buy_rate} - بيع {rate.sell_rate}'
                    )
        
        # عرض أفضل الأسعار
        self.stdout.write('\nأفضل الأسعار:')
        for currency_code in currencies:
            best_rates = currency_service.get_best_rates(currency_code)
            if best_rates:
                self.stdout.write(
                    f'{currency_code}: أفضل شراء {best_rates["best_buy"]["rate"]} '
                    f'({best_rates["best_buy"]["bank"]}) - '
                    f'أفضل بيع {best_rates["best_sell"]["rate"]} '
                    f'({best_rates["best_sell"]["bank"]})'
                )
