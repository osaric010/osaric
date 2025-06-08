from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from services.models import SystemSettings
import json

register = template.Library()


@register.simple_tag
def get_setting(key, default=None):
    """جلب قيمة إعداد من النظام"""
    try:
        setting = SystemSettings.objects.get(key=key)
        if setting.value_type == 'BOOLEAN':
            return setting.value.lower() == 'true'
        elif setting.value_type == 'INTEGER':
            return int(setting.value)
        elif setting.value_type == 'FLOAT':
            return float(setting.value)
        else:
            return setting.value
    except SystemSettings.DoesNotExist:
        return default


@register.simple_tag
def format_currency(amount, currency_symbol=None):
    """تنسيق المبلغ بالعملة"""
    try:
        if currency_symbol is None:
            currency_symbol = get_setting('currency_symbol', 'ر.س')
        
        decimal_places = get_setting('decimal_places', 2)
        
        # تنسيق الرقم
        formatted_amount = f"{float(amount):,.{decimal_places}f}"
        
        return f"{formatted_amount} {currency_symbol}"
    except (ValueError, TypeError):
        return str(amount)


@register.simple_tag
def company_info(field):
    """جلب معلومات الشركة"""
    field_mapping = {
        'name': 'company_name',
        'address': 'company_address',
        'phone': 'company_phone',
        'email': 'company_email',
        'logo': 'company_logo',
    }
    
    key = field_mapping.get(field)
    if key:
        return get_setting(key)
    return None


@register.simple_tag
def tax_amount(amount, tax_rate=None):
    """حساب مبلغ الضريبة"""
    try:
        if tax_rate is None:
            tax_rate = get_setting('tax_rate', 15.0)
        
        tax = float(amount) * (float(tax_rate) / 100)
        decimal_places = get_setting('decimal_places', 2)
        
        return round(tax, decimal_places)
    except (ValueError, TypeError):
        return 0


@register.simple_tag
def total_with_tax(amount, tax_rate=None):
    """حساب المجموع مع الضريبة"""
    try:
        tax = tax_amount(amount, tax_rate)
        total = float(amount) + tax
        decimal_places = get_setting('decimal_places', 2)
        
        return round(total, decimal_places)
    except (ValueError, TypeError):
        return amount


@register.filter
def apply_decimal_places(value):
    """تطبيق عدد الخانات العشرية"""
    try:
        decimal_places = get_setting('decimal_places', 2)
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return value


@register.inclusion_tag('tags/company_header.html')
def company_header():
    """رأس الشركة للطباعة"""
    return {
        'company_name': get_setting('company_name', 'شركة أوساريك للحسابات'),
        'company_address': get_setting('company_address'),
        'company_phone': get_setting('company_phone'),
        'company_email': get_setting('company_email'),
        'company_logo': get_setting('company_logo'),
        'tax_number': get_setting('tax_number'),
        'show_logo': get_setting('print_logo', True),
        'show_company_info': get_setting('print_company_info', True),
    }


@register.inclusion_tag('tags/invoice_footer.html')
def invoice_footer():
    """تذييل الفاتورة"""
    return {
        'show_terms': get_setting('print_terms', True),
        'show_signature': get_setting('print_signature', False),
        'company_name': get_setting('company_name', 'شركة أوساريك للحسابات'),
    }


@register.simple_tag
def pagination_size():
    """حجم الصفحة للجداول"""
    return get_setting('ui_records_per_page', 25)


@register.simple_tag
def is_feature_enabled(feature):
    """فحص تفعيل ميزة معينة"""
    feature_mapping = {
        'multi_currency': 'enable_multi_currency',
        'branches': 'enable_branches',
        'dark_mode': 'ui_enable_dark_mode',
        'animations': 'ui_enable_animations',
        'notifications': 'ui_enable_notifications',
        'tooltips': 'ui_show_tooltips',
        'breadcrumbs': 'ui_enable_breadcrumbs',
    }
    
    key = feature_mapping.get(feature)
    if key:
        return get_setting(key, False)
    return False


@register.simple_tag
def get_theme_color(color_type):
    """جلب ألوان المظهر"""
    color_mapping = {
        'primary': 'ui_primary_color',
        'secondary': 'ui_secondary_color',
        'success': 'ui_success_color',
        'danger': 'ui_danger_color',
        'warning': 'ui_warning_color',
        'info': 'ui_info_color',
    }
    
    key = color_mapping.get(color_type)
    if key:
        return get_setting(key)
    return None


@register.simple_tag
def numbering_format(document_type, number):
    """تنسيق ترقيم المستندات"""
    try:
        if document_type == 'sales':
            prefix = get_setting('sales_number_prefix', 'INV')
            length = get_setting('sales_number_length', 6)
        elif document_type == 'purchase':
            prefix = get_setting('purchase_number_prefix', 'PUR')
            length = get_setting('purchase_number_length', 6)
        else:
            return str(number)
        
        # تنسيق الرقم بالطول المحدد
        formatted_number = str(number).zfill(length)
        return f"{prefix}{formatted_number}"
    except:
        return str(number)


@register.filter
def json_decode(value):
    """فك تشفير JSON"""
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}


@register.simple_tag
def system_status():
    """حالة النظام"""
    try:
        total_settings = SystemSettings.objects.count()
        active_settings = SystemSettings.objects.filter(is_editable=True).count()
        
        return {
            'total_settings': total_settings,
            'active_settings': active_settings,
            'system_version': get_setting('system_version', '1.0.0'),
            'install_date': get_setting('system_install_date'),
        }
    except:
        return {
            'total_settings': 0,
            'active_settings': 0,
            'system_version': '1.0.0',
            'install_date': None,
        }


@register.simple_tag
def fiscal_year_info():
    """معلومات السنة المالية"""
    from datetime import datetime, date
    
    try:
        fiscal_start = get_setting('fiscal_year_start', '01-01')
        current_year = datetime.now().year
        
        # تحويل تاريخ بداية السنة المالية
        month, day = map(int, fiscal_start.split('-'))
        fiscal_start_date = date(current_year, month, day)
        
        # تحديد السنة المالية الحالية
        today = date.today()
        if today >= fiscal_start_date:
            fiscal_year = current_year
        else:
            fiscal_year = current_year - 1
        
        return {
            'fiscal_year': fiscal_year,
            'start_date': fiscal_start_date.replace(year=fiscal_year),
            'end_date': fiscal_start_date.replace(year=fiscal_year + 1) - timedelta(days=1),
        }
    except:
        return {
            'fiscal_year': datetime.now().year,
            'start_date': date(datetime.now().year, 1, 1),
            'end_date': date(datetime.now().year, 12, 31),
        }


@register.simple_tag
def barcode_settings():
    """إعدادات الباركود"""
    return {
        'type': get_setting('barcode_type', 'CODE128'),
        'width': get_setting('barcode_width', 2),
        'height': get_setting('barcode_height', 50),
        'show_text': get_setting('barcode_show_text', True),
    }


@register.simple_tag(takes_context=True)
def user_permissions(context):
    """صلاحيات المستخدم الحالي"""
    request = context.get('request')
    if request and request.user.is_authenticated:
        return {
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
            'groups': list(request.user.groups.values_list('name', flat=True)),
            'permissions': list(request.user.user_permissions.values_list('codename', flat=True)),
        }
    return {
        'is_staff': False,
        'is_superuser': False,
        'groups': [],
        'permissions': [],
    }
