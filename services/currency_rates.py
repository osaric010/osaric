"""
خدمة جلب أسعار العملات من البنوك المصرية
"""

import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from definitions.models import Currency, EgyptianBankRate, CurrencyRateHistory
import logging

logger = logging.getLogger(__name__)


class EgyptianBankRatesService:
    """خدمة جلب أسعار العملات من البنوك المصرية"""
    
    # البنوك المصرية الرئيسية
    EGYPTIAN_BANKS = {
        'NBE': 'البنك الأهلي المصري',
        'CIB': 'البنك التجاري الدولي',
        'AAIB': 'البنك العربي الأفريقي الدولي',
        'QNB': 'بنك قطر الوطني الأهلي',
        'ADIB': 'مصرف أبوظبي الإسلامي',
        'ALEXBANK': 'بنك الإسكندرية',
        'MIDB': 'بنك التنمية الصناعية',
        'CAE': 'بنك كريدي أجريكول',
        'HSBC': 'بنك إتش إس بي سي',
        'SCB': 'بنك ستاندرد تشارترد',
    }
    
    # العملات المدعومة
    SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'SAR', 'AED', 'KWD', 'QAR', 'OMR', 'BHD', 'JOD']
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_cbe_rates(self):
        """جلب أسعار البنك المركزي المصري"""
        try:
            # API البنك المركزي المصري (مثال)
            url = "https://www.cbe.org.eg/en/economic-research/statistics/exchange-rates"
            
            # بيانات تجريبية (في التطبيق الحقيقي يتم جلبها من API)
            mock_rates = {
                'USD': {'buy': 30.85, 'sell': 30.95},
                'EUR': {'buy': 33.45, 'sell': 33.55},
                'GBP': {'buy': 39.15, 'sell': 39.25},
                'SAR': {'buy': 8.22, 'sell': 8.26},
                'AED': {'buy': 8.39, 'sell': 8.43},
                'KWD': {'buy': 100.45, 'sell': 100.65},
                'QAR': {'buy': 8.47, 'sell': 8.51},
                'OMR': {'buy': 80.25, 'sell': 80.45},
                'BHD': {'buy': 81.85, 'sell': 82.05},
                'JOD': {'buy': 43.55, 'sell': 43.65},
            }
            
            return self._save_bank_rates('البنك المركزي المصري', mock_rates)
            
        except Exception as e:
            logger.error(f"خطأ في جلب أسعار البنك المركزي: {str(e)}")
            return False
    
    def get_nbe_rates(self):
        """جلب أسعار البنك الأهلي المصري"""
        try:
            # بيانات تجريبية للبنك الأهلي
            mock_rates = {
                'USD': {'buy': 30.80, 'sell': 31.00},
                'EUR': {'buy': 33.40, 'sell': 33.60},
                'GBP': {'buy': 39.10, 'sell': 39.30},
                'SAR': {'buy': 8.20, 'sell': 8.28},
                'AED': {'buy': 8.37, 'sell': 8.45},
                'KWD': {'buy': 100.40, 'sell': 100.70},
                'QAR': {'buy': 8.45, 'sell': 8.53},
                'OMR': {'buy': 80.20, 'sell': 80.50},
                'BHD': {'buy': 81.80, 'sell': 82.10},
                'JOD': {'buy': 43.50, 'sell': 43.70},
            }
            
            return self._save_bank_rates('البنك الأهلي المصري', mock_rates)
            
        except Exception as e:
            logger.error(f"خطأ في جلب أسعار البنك الأهلي: {str(e)}")
            return False
    
    def get_cib_rates(self):
        """جلب أسعار البنك التجاري الدولي"""
        try:
            # بيانات تجريبية للبنك التجاري الدولي
            mock_rates = {
                'USD': {'buy': 30.82, 'sell': 30.98},
                'EUR': {'buy': 33.42, 'sell': 33.58},
                'GBP': {'buy': 39.12, 'sell': 39.28},
                'SAR': {'buy': 8.21, 'sell': 8.27},
                'AED': {'buy': 8.38, 'sell': 8.44},
                'KWD': {'buy': 100.42, 'sell': 100.68},
                'QAR': {'buy': 8.46, 'sell': 8.52},
                'OMR': {'buy': 80.22, 'sell': 80.48},
                'BHD': {'buy': 81.82, 'sell': 82.08},
                'JOD': {'buy': 43.52, 'sell': 43.68},
            }
            
            return self._save_bank_rates('البنك التجاري الدولي', mock_rates)
            
        except Exception as e:
            logger.error(f"خطأ في جلب أسعار البنك التجاري الدولي: {str(e)}")
            return False
    
    def get_qnb_rates(self):
        """جلب أسعار بنك قطر الوطني الأهلي"""
        try:
            # بيانات تجريبية لبنك قطر الوطني
            mock_rates = {
                'USD': {'buy': 30.83, 'sell': 30.97},
                'EUR': {'buy': 33.43, 'sell': 33.57},
                'GBP': {'buy': 39.13, 'sell': 39.27},
                'SAR': {'buy': 8.22, 'sell': 8.26},
                'AED': {'buy': 8.39, 'sell': 8.43},
                'KWD': {'buy': 100.43, 'sell': 100.67},
                'QAR': {'buy': 8.47, 'sell': 8.51},
                'OMR': {'buy': 80.23, 'sell': 80.47},
                'BHD': {'buy': 81.83, 'sell': 82.07},
                'JOD': {'buy': 43.53, 'sell': 43.67},
            }
            
            return self._save_bank_rates('بنك قطر الوطني الأهلي', mock_rates)
            
        except Exception as e:
            logger.error(f"خطأ في جلب أسعار بنك قطر الوطني: {str(e)}")
            return False
    
    def _save_bank_rates(self, bank_name, rates_data):
        """حفظ أسعار البنك في قاعدة البيانات"""
        try:
            saved_count = 0
            
            for currency_code, rates in rates_data.items():
                try:
                    currency = Currency.objects.get(code=currency_code, is_active=True)
                    
                    # حفظ أو تحديث سعر البنك
                    bank_rate, created = EgyptianBankRate.objects.update_or_create(
                        currency=currency,
                        bank_name=bank_name,
                        defaults={
                            'buy_rate': Decimal(str(rates['buy'])),
                            'sell_rate': Decimal(str(rates['sell'])),
                            'is_active': True,
                        }
                    )
                    
                    # حفظ في تاريخ الأسعار
                    CurrencyRateHistory.objects.create(
                        currency=currency,
                        rate=bank_rate.average_rate,
                        rate_type='AVERAGE',
                        source=bank_name,
                        recorded_date=timezone.now()
                    )
                    
                    saved_count += 1
                    
                except Currency.DoesNotExist:
                    logger.warning(f"العملة {currency_code} غير موجودة")
                    continue
            
            logger.info(f"تم حفظ {saved_count} سعر من {bank_name}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حفظ أسعار {bank_name}: {str(e)}")
            return False
    
    def update_all_rates(self):
        """تحديث أسعار جميع البنوك"""
        results = {
            'success': 0,
            'failed': 0,
            'banks': []
        }
        
        # قائمة البنوك ودوالها
        banks_methods = [
            ('البنك المركزي المصري', self.get_cbe_rates),
            ('البنك الأهلي المصري', self.get_nbe_rates),
            ('البنك التجاري الدولي', self.get_cib_rates),
            ('بنك قطر الوطني الأهلي', self.get_qnb_rates),
        ]
        
        for bank_name, method in banks_methods:
            try:
                if method():
                    results['success'] += 1
                    results['banks'].append({'name': bank_name, 'status': 'success'})
                else:
                    results['failed'] += 1
                    results['banks'].append({'name': bank_name, 'status': 'failed'})
            except Exception as e:
                results['failed'] += 1
                results['banks'].append({'name': bank_name, 'status': 'error', 'error': str(e)})
                logger.error(f"خطأ في تحديث {bank_name}: {str(e)}")
        
        return results
    
    def get_latest_rates(self, currency_code=None):
        """جلب أحدث الأسعار"""
        query = EgyptianBankRate.objects.filter(is_active=True).select_related('currency')
        
        if currency_code:
            query = query.filter(currency__code=currency_code)
        
        return query.order_by('currency__code', 'bank_name')
    
    def get_best_rates(self, currency_code):
        """جلب أفضل الأسعار لعملة معينة"""
        rates = self.get_latest_rates(currency_code)
        
        if not rates:
            return None
        
        best_buy = rates.order_by('-buy_rate').first()  # أعلى سعر شراء
        best_sell = rates.order_by('sell_rate').first()  # أقل سعر بيع
        
        return {
            'currency': currency_code,
            'best_buy': {
                'rate': best_buy.buy_rate,
                'bank': best_buy.bank_name
            },
            'best_sell': {
                'rate': best_sell.sell_rate,
                'bank': best_sell.bank_name
            },
            'average': rates.aggregate(
                avg_buy=models.Avg('buy_rate'),
                avg_sell=models.Avg('sell_rate')
            )
        }


# إنشاء instance عام للخدمة
currency_service = EgyptianBankRatesService()
