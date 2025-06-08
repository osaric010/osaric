from .models import CompanySettings


def company_settings(request):
    """Context processor لإعدادات الشركة"""
    try:
        settings = CompanySettings.get_settings()
        return {
            'company_settings': settings,
            'company_logo_url': settings.logo_url,
            'company_name': settings.company_name,
            'app_name': settings.app_name,
            'app_version': settings.app_version,
        }
    except Exception:
        # في حالة عدم وجود إعدادات أو حدوث خطأ
        return {
            'company_settings': None,
            'company_logo_url': None,
            'company_name': 'نظام الحسابات',
            'app_name': 'نظام الحسابات',
            'app_version': '1.0.0',
        }
