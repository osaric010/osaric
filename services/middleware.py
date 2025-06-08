from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from .models import SystemSettings
import logging

logger = logging.getLogger(__name__)


class SystemSettingsMiddleware(MiddlewareMixin):
    """Middleware لتطبيق إعدادات النظام"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cached_settings = {}
        self.cache_time = None
        super().__init__(get_response)
    
    def process_request(self, request):
        """معالجة الطلب وتطبيق الإعدادات"""
        try:
            # تحديث cache الإعدادات كل 5 دقائق
            now = timezone.now()
            if not self.cache_time or (now - self.cache_time).seconds > 300:
                self.update_settings_cache()
                self.cache_time = now
            
            # تطبيق إعدادات الجلسة
            self.apply_session_settings(request)
            
            # تطبيق إعدادات الأمان
            self.apply_security_settings(request)
            
        except Exception as e:
            logger.error(f"خطأ في SystemSettingsMiddleware: {e}")
    
    def update_settings_cache(self):
        """تحديث cache الإعدادات"""
        try:
            self.cached_settings = {}
            for setting in SystemSettings.objects.all():
                if setting.value_type == 'BOOLEAN':
                    value = setting.value.lower() == 'true'
                elif setting.value_type == 'INTEGER':
                    try:
                        value = int(setting.value)
                    except (ValueError, TypeError):
                        value = 0
                elif setting.value_type == 'FLOAT':
                    try:
                        value = float(setting.value)
                    except (ValueError, TypeError):
                        value = 0.0
                else:
                    value = setting.value
                
                self.cached_settings[setting.key] = value
        except Exception as e:
            logger.error(f"خطأ في تحديث cache الإعدادات: {e}")
    
    def apply_session_settings(self, request):
        """تطبيق إعدادات الجلسة"""
        try:
            session_timeout = self.cached_settings.get('session_timeout', 30)
            
            if request.user.is_authenticated:
                # تحديث مهلة انتهاء الجلسة
                request.session.set_expiry(session_timeout * 60)  # تحويل إلى ثواني
                
                # تنظيف الجلسات المنتهية الصلاحية
                if hasattr(request, '_session_cleanup_done'):
                    return
                
                expired_sessions = Session.objects.filter(
                    expire_date__lt=timezone.now()
                )
                expired_sessions.delete()
                request._session_cleanup_done = True
                
        except Exception as e:
            logger.error(f"خطأ في تطبيق إعدادات الجلسة: {e}")
    
    def apply_security_settings(self, request):
        """تطبيق إعدادات الأمان"""
        try:
            # تطبيق إعدادات كلمة المرور (للمستخدمين الجدد)
            password_settings = {
                'min_length': self.cached_settings.get('password_min_length', 8),
                'require_uppercase': self.cached_settings.get('password_require_uppercase', True),
                'require_numbers': self.cached_settings.get('password_require_numbers', True),
                'require_symbols': self.cached_settings.get('password_require_symbols', False),
            }
            
            # حفظ إعدادات كلمة المرور في الجلسة
            request.session['password_settings'] = password_settings
            
            # تطبيق إعدادات الحد الأقصى للمستخدمين
            max_users = self.cached_settings.get('max_users', 50)
            request.session['max_users'] = max_users
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق إعدادات الأمان: {e}")


class CompanyInfoMiddleware(MiddlewareMixin):
    """Middleware لمعلومات الشركة"""
    
    def process_request(self, request):
        """إضافة معلومات الشركة للطلب"""
        try:
            company_info = {
                'name': SystemSettings.objects.filter(key='company_name').first(),
                'address': SystemSettings.objects.filter(key='company_address').first(),
                'phone': SystemSettings.objects.filter(key='company_phone').first(),
                'email': SystemSettings.objects.filter(key='company_email').first(),
                'logo': SystemSettings.objects.filter(key='company_logo').first(),
            }
            
            # تحويل القيم
            for key, setting in company_info.items():
                if setting:
                    company_info[key] = setting.value
                else:
                    company_info[key] = None
            
            request.company_info = company_info
            
        except Exception as e:
            logger.error(f"خطأ في CompanyInfoMiddleware: {e}")
            request.company_info = {
                'name': 'شركة أوساريك للحسابات',
                'address': None,
                'phone': None,
                'email': None,
                'logo': None,
            }


class UISettingsMiddleware(MiddlewareMixin):
    """Middleware لإعدادات الواجهة"""
    
    def process_request(self, request):
        """تطبيق إعدادات الواجهة"""
        try:
            # جلب إعدادات الواجهة
            ui_settings = {}
            ui_settings_qs = SystemSettings.objects.filter(
                category='واجهة المستخدم'
            )
            
            for setting in ui_settings_qs:
                if setting.value_type == 'BOOLEAN':
                    value = setting.value.lower() == 'true'
                elif setting.value_type == 'INTEGER':
                    try:
                        value = int(setting.value)
                    except (ValueError, TypeError):
                        value = 0
                else:
                    value = setting.value
                
                ui_settings[setting.key] = value
            
            # تطبيق إعدادات اللغة
            language = ui_settings.get('system_language', 'ar')
            if hasattr(request, 'session'):
                request.session['django_language'] = language
            
            # تطبيق إعدادات المنطقة الزمنية
            timezone_setting = SystemSettings.objects.filter(key='timezone').first()
            if timezone_setting:
                request.session['django_timezone'] = timezone_setting.value
            
            request.ui_settings = ui_settings
            
        except Exception as e:
            logger.error(f"خطأ في UISettingsMiddleware: {e}")
            request.ui_settings = {}


class FinancialSettingsMiddleware(MiddlewareMixin):
    """Middleware للإعدادات المالية"""
    
    def process_request(self, request):
        """تطبيق الإعدادات المالية"""
        try:
            financial_settings = {}
            
            # جلب الإعدادات المالية
            financial_keys = [
                'default_currency', 'currency_symbol', 'decimal_places',
                'tax_rate', 'tax_number', 'fiscal_year_start'
            ]
            
            for key in financial_keys:
                setting = SystemSettings.objects.filter(key=key).first()
                if setting:
                    if setting.value_type == 'INTEGER':
                        financial_settings[key] = int(setting.value)
                    elif setting.value_type == 'FLOAT':
                        financial_settings[key] = float(setting.value)
                    else:
                        financial_settings[key] = setting.value
            
            request.financial_settings = financial_settings
            
        except Exception as e:
            logger.error(f"خطأ في FinancialSettingsMiddleware: {e}")
            request.financial_settings = {
                'default_currency': 'EGP',
                'currency_symbol': 'ج.م',
                'decimal_places': 2,
                'tax_rate': 14.0,
            }


class PrintSettingsMiddleware(MiddlewareMixin):
    """Middleware لإعدادات الطباعة"""
    
    def process_request(self, request):
        """تطبيق إعدادات الطباعة"""
        try:
            print_settings = {}
            
            # جلب إعدادات الطباعة
            print_keys = [
                'print_template', 'print_logo', 'print_company_info',
                'print_terms', 'print_signature', 'print_copies'
            ]
            
            for key in print_keys:
                setting = SystemSettings.objects.filter(key=key).first()
                if setting:
                    if setting.value_type == 'BOOLEAN':
                        print_settings[key] = setting.value.lower() == 'true'
                    elif setting.value_type == 'INTEGER':
                        print_settings[key] = int(setting.value)
                    else:
                        print_settings[key] = setting.value
            
            request.print_settings = print_settings
            
        except Exception as e:
            logger.error(f"خطأ في PrintSettingsMiddleware: {e}")
            request.print_settings = {
                'print_template': 'default',
                'print_logo': True,
                'print_company_info': True,
                'print_terms': True,
                'print_signature': False,
                'print_copies': 1,
            }
