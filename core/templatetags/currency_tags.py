"""
Template tags للعملة
Currency template tags
"""

from django import template
from django.utils.safestring import mark_safe
from core.currency_utils import (
    format_currency, 
    get_currency_symbol, 
    get_currency_name,
    get_default_currency,
    convert_currency
)

register = template.Library()


@register.filter
def currency(value, currency_code=None):
    """
    تنسيق المبلغ بالعملة
    Usage: {{ amount|currency }}
           {{ amount|currency:"USD" }}
    """
    return format_currency(value, currency_code=currency_code)


@register.filter
def currency_symbol_only(value, currency_code=None):
    """
    تنسيق المبلغ مع رمز العملة فقط
    Usage: {{ amount|currency_symbol_only }}
    """
    return format_currency(value, currency_code=currency_code, show_symbol=True, show_code=False)


@register.filter
def currency_code_only(value, currency_code=None):
    """
    تنسيق المبلغ مع كود العملة فقط
    Usage: {{ amount|currency_code_only }}
    """
    return format_currency(value, currency_code=currency_code, show_symbol=False, show_code=True)


@register.filter
def currency_full(value, currency_code=None):
    """
    تنسيق المبلغ مع رمز وكود العملة
    Usage: {{ amount|currency_full }}
    """
    return format_currency(value, currency_code=currency_code, show_symbol=True, show_code=True)


@register.filter
def no_currency(value):
    """
    تنسيق المبلغ بدون رمز العملة
    Usage: {{ amount|no_currency }}
    """
    return format_currency(value, show_symbol=False, show_code=False)


@register.filter
def convert_to_currency(value, target_currency):
    """
    تحويل المبلغ إلى عملة أخرى
    Usage: {{ amount|convert_to_currency:"USD" }}
    """
    default_currency = get_default_currency()
    if default_currency:
        converted = convert_currency(value, default_currency.code, target_currency)
        return format_currency(converted, currency_code=target_currency)
    return format_currency(value)


@register.simple_tag
def currency_symbol():
    """
    الحصول على رمز العملة الافتراضية
    Usage: {% currency_symbol %}
    """
    return get_currency_symbol()


@register.simple_tag
def currency_name():
    """
    الحصول على اسم العملة الافتراضية
    Usage: {% currency_name %}
    """
    return get_currency_name()


@register.simple_tag
def default_currency():
    """
    الحصول على العملة الافتراضية
    Usage: {% default_currency %}
    """
    currency = get_default_currency()
    return currency if currency else None


@register.inclusion_tag('core/currency_display.html')
def currency_display(amount, currency_code=None, size='normal', color='primary'):
    """
    عرض المبلغ بتنسيق جميل
    Usage: {% currency_display amount %}
           {% currency_display amount "USD" "large" "success" %}
    """
    formatted_amount = format_currency(amount, currency_code=currency_code)
    
    return {
        'amount': amount,
        'formatted_amount': formatted_amount,
        'currency_code': currency_code,
        'size': size,
        'color': color
    }


@register.inclusion_tag('core/currency_input.html')
def currency_input(field_name, value=None, currency_code=None, required=False, placeholder=None):
    """
    حقل إدخال للمبالغ مع رمز العملة
    Usage: {% currency_input "amount" value "EGP" True "أدخل المبلغ" %}
    """
    symbol = get_currency_symbol()
    if currency_code:
        try:
            from definitions.models import Currency
            currency = Currency.objects.get(code=currency_code, is_active=True)
            symbol = currency.symbol
        except:
            pass
    
    return {
        'field_name': field_name,
        'value': value or '',
        'currency_symbol': symbol,
        'required': required,
        'placeholder': placeholder or 'أدخل المبلغ'
    }


@register.filter
def multiply_currency(value, multiplier):
    """
    ضرب المبلغ في رقم وتنسيقه
    Usage: {{ amount|multiply_currency:quantity }}
    """
    if value is None or multiplier is None:
        return format_currency(0)
    
    try:
        result = float(value) * float(multiplier)
        return format_currency(result)
    except (ValueError, TypeError):
        return format_currency(0)


@register.filter
def add_currency(value1, value2):
    """
    جمع مبلغين وتنسيقهما
    Usage: {{ amount1|add_currency:amount2 }}
    """
    if value1 is None:
        value1 = 0
    if value2 is None:
        value2 = 0
    
    try:
        result = float(value1) + float(value2)
        return format_currency(result)
    except (ValueError, TypeError):
        return format_currency(0)


@register.filter
def subtract_currency(value1, value2):
    """
    طرح مبلغين وتنسيقهما
    Usage: {{ amount1|subtract_currency:amount2 }}
    """
    if value1 is None:
        value1 = 0
    if value2 is None:
        value2 = 0
    
    try:
        result = float(value1) - float(value2)
        return format_currency(result)
    except (ValueError, TypeError):
        return format_currency(0)


@register.filter
def percentage_of_currency(value, percentage):
    """
    حساب نسبة مئوية من المبلغ
    Usage: {{ amount|percentage_of_currency:15 }}  # 15%
    """
    if value is None or percentage is None:
        return format_currency(0)
    
    try:
        result = float(value) * (float(percentage) / 100)
        return format_currency(result)
    except (ValueError, TypeError):
        return format_currency(0)


@register.filter
def currency_abs(value):
    """
    القيمة المطلقة للمبلغ
    Usage: {{ amount|currency_abs }}
    """
    if value is None:
        return format_currency(0)
    
    try:
        result = abs(float(value))
        return format_currency(result)
    except (ValueError, TypeError):
        return format_currency(0)


@register.filter
def is_positive_currency(value):
    """
    التحقق من أن المبلغ موجب
    Usage: {% if amount|is_positive_currency %}
    """
    if value is None:
        return False
    
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False


@register.filter
def is_negative_currency(value):
    """
    التحقق من أن المبلغ سالب
    Usage: {% if amount|is_negative_currency %}
    """
    if value is None:
        return False
    
    try:
        return float(value) < 0
    except (ValueError, TypeError):
        return False


@register.filter
def currency_color_class(value):
    """
    إرجاع CSS class حسب قيمة المبلغ
    Usage: <span class="{{ amount|currency_color_class }}">
    """
    if value is None:
        return 'text-muted'
    
    try:
        amount = float(value)
        if amount > 0:
            return 'text-success'
        elif amount < 0:
            return 'text-danger'
        else:
            return 'text-muted'
    except (ValueError, TypeError):
        return 'text-muted'


@register.simple_tag
def currency_rate(from_currency, to_currency=None):
    """
    الحصول على سعر الصرف
    Usage: {% currency_rate "USD" "EGP" %}
    """
    from core.currency_utils import get_exchange_rate
    return get_exchange_rate(from_currency, to_currency)
