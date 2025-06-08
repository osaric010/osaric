"""
أدوات العملة - Currency Utilities
وظائف مساعدة للتعامل مع العملات وتنسيق الأرقام
"""

from decimal import Decimal
from django.conf import settings
from definitions.models import Currency
from services.models import SystemSettings


def get_default_currency():
    """الحصول على العملة الافتراضية"""
    try:
        # البحث عن العملة الأساسية
        currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
        if currency:
            return currency
        
        # إذا لم توجد، البحث عن الجنيه المصري
        currency = Currency.objects.filter(code='EGP', is_active=True).first()
        if currency:
            return currency
        
        # إذا لم توجد، إنشاء الجنيه المصري
        currency = Currency.objects.create(
            code='EGP',
            name='الجنيه المصري',
            symbol='ج.م',
            exchange_rate=Decimal('1.0000'),
            is_base_currency=True,
            is_active=True
        )
        return currency
        
    except Exception:
        # في حالة عدم وجود جدول العملات، إرجاع قيم افتراضية
        return None


def get_currency_symbol():
    """الحصول على رمز العملة الافتراضية"""
    try:
        setting = SystemSettings.objects.filter(key='currency_symbol').first()
        if setting:
            return setting.value
    except:
        pass
    
    currency = get_default_currency()
    return currency.symbol if currency else 'ج.م'


def get_currency_name():
    """الحصول على اسم العملة الافتراضية"""
    try:
        setting = SystemSettings.objects.filter(key='currency_name').first()
        if setting:
            return setting.value
    except:
        pass
    
    currency = get_default_currency()
    return currency.name if currency else 'الجنيه المصري'


def get_decimal_places():
    """الحصول على عدد الخانات العشرية"""
    try:
        setting = SystemSettings.objects.filter(key='decimal_places').first()
        if setting:
            return int(setting.value)
    except:
        pass
    return 2


def get_thousands_separator():
    """الحصول على فاصل الآلاف"""
    try:
        setting = SystemSettings.objects.filter(key='thousands_separator').first()
        if setting:
            return setting.value
    except:
        pass
    return ','


def get_decimal_separator():
    """الحصول على فاصل العشرية"""
    try:
        setting = SystemSettings.objects.filter(key='decimal_separator').first()
        if setting:
            return setting.value
    except:
        pass
    return '.'


def get_currency_position():
    """الحصول على موضع رمز العملة (before/after)"""
    try:
        setting = SystemSettings.objects.filter(key='currency_position').first()
        if setting:
            return setting.value
    except:
        pass
    return 'after'


def format_currency(amount, currency_code=None, show_symbol=True, show_code=False):
    """
    تنسيق المبلغ بالعملة
    
    Args:
        amount: المبلغ (رقم أو Decimal)
        currency_code: رمز العملة (اختياري)
        show_symbol: إظهار رمز العملة
        show_code: إظهار كود العملة
    
    Returns:
        str: المبلغ منسق
    """
    if amount is None:
        amount = 0
    
    # تحويل إلى Decimal
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    # الحصول على إعدادات التنسيق
    decimal_places = get_decimal_places()
    thousands_sep = get_thousands_separator()
    decimal_sep = get_decimal_separator()
    currency_position = get_currency_position()
    
    # تنسيق الرقم
    # تقريب الرقم حسب عدد الخانات العشرية
    amount = amount.quantize(Decimal('0.' + '0' * decimal_places))
    
    # تحويل إلى نص
    amount_str = f"{amount:.{decimal_places}f}"
    
    # تقسيم الجزء الصحيح والعشري
    if '.' in amount_str:
        integer_part, decimal_part = amount_str.split('.')
    else:
        integer_part = amount_str
        decimal_part = '0' * decimal_places
    
    # إضافة فاصل الآلاف
    if len(integer_part) > 3:
        # تقسيم الرقم إلى مجموعات من 3 أرقام
        groups = []
        for i in range(len(integer_part), 0, -3):
            start = max(0, i - 3)
            groups.append(integer_part[start:i])
        integer_part = thousands_sep.join(reversed(groups))
    
    # تجميع الرقم
    if decimal_places > 0 and decimal_part != '0' * decimal_places:
        formatted_amount = f"{integer_part}{decimal_sep}{decimal_part}"
    else:
        formatted_amount = integer_part
    
    # إضافة رمز العملة
    if show_symbol or show_code:
        if currency_code:
            try:
                currency = Currency.objects.get(code=currency_code, is_active=True)
                symbol = currency.symbol
                code = currency.code
            except Currency.DoesNotExist:
                symbol = get_currency_symbol()
                code = 'EGP'
        else:
            symbol = get_currency_symbol()
            code = get_default_currency().code if get_default_currency() else 'EGP'
        
        # تحديد النص المراد إضافته
        currency_text = ''
        if show_symbol and show_code:
            currency_text = f"{symbol} ({code})"
        elif show_symbol:
            currency_text = symbol
        elif show_code:
            currency_text = code
        
        # تحديد موضع العملة
        if currency_position == 'before':
            formatted_amount = f"{currency_text} {formatted_amount}"
        else:  # after
            formatted_amount = f"{formatted_amount} {currency_text}"
    
    return formatted_amount


def convert_currency(amount, from_currency, to_currency=None):
    """
    تحويل العملة
    
    Args:
        amount: المبلغ
        from_currency: العملة المصدر (كود أو كائن)
        to_currency: العملة الهدف (كود أو كائن، افتراضي: العملة الأساسية)
    
    Returns:
        Decimal: المبلغ محول
    """
    if amount is None or amount == 0:
        return Decimal('0')
    
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    # الحصول على كائن العملة المصدر
    if isinstance(from_currency, str):
        try:
            from_curr = Currency.objects.get(code=from_currency, is_active=True)
        except Currency.DoesNotExist:
            return amount  # إرجاع المبلغ كما هو إذا لم توجد العملة
    else:
        from_curr = from_currency
    
    # الحصول على كائن العملة الهدف
    if to_currency is None:
        to_curr = get_default_currency()
    elif isinstance(to_currency, str):
        try:
            to_curr = Currency.objects.get(code=to_currency, is_active=True)
        except Currency.DoesNotExist:
            to_curr = get_default_currency()
    else:
        to_curr = to_currency
    
    if not to_curr:
        return amount
    
    # إذا كانت العملتان متشابهتان
    if from_curr.code == to_curr.code:
        return amount
    
    # تحويل إلى العملة الأساسية أولاً
    if from_curr.is_base_currency:
        base_amount = amount
    else:
        base_amount = amount / from_curr.exchange_rate
    
    # تحويل من العملة الأساسية إلى العملة الهدف
    if to_curr.is_base_currency:
        converted_amount = base_amount
    else:
        converted_amount = base_amount * to_curr.exchange_rate
    
    return converted_amount


def get_exchange_rate(from_currency, to_currency=None):
    """
    الحصول على سعر الصرف بين عملتين
    
    Args:
        from_currency: العملة المصدر
        to_currency: العملة الهدف (افتراضي: العملة الأساسية)
    
    Returns:
        Decimal: سعر الصرف
    """
    if to_currency is None:
        to_currency = get_default_currency()
    
    if isinstance(from_currency, str):
        try:
            from_curr = Currency.objects.get(code=from_currency, is_active=True)
        except Currency.DoesNotExist:
            return Decimal('1')
    else:
        from_curr = from_currency
    
    if isinstance(to_currency, str):
        try:
            to_curr = Currency.objects.get(code=to_currency, is_active=True)
        except Currency.DoesNotExist:
            return Decimal('1')
    else:
        to_curr = to_currency
    
    if from_curr.code == to_curr.code:
        return Decimal('1')
    
    # حساب سعر الصرف
    if from_curr.is_base_currency:
        return to_curr.exchange_rate
    elif to_curr.is_base_currency:
        return Decimal('1') / from_curr.exchange_rate
    else:
        # تحويل عبر العملة الأساسية
        return to_curr.exchange_rate / from_curr.exchange_rate


def update_exchange_rates(rates_dict):
    """
    تحديث أسعار الصرف
    
    Args:
        rates_dict: قاموس بأسعار الصرف {currency_code: rate}
    """
    for currency_code, rate in rates_dict.items():
        try:
            currency = Currency.objects.get(code=currency_code, is_active=True)
            if not currency.is_base_currency:  # لا نحدث سعر العملة الأساسية
                currency.exchange_rate = Decimal(str(rate))
                currency.save()
        except Currency.DoesNotExist:
            continue


def get_currency_choices():
    """الحصول على خيارات العملات للنماذج"""
    try:
        currencies = Currency.objects.filter(is_active=True).order_by('name')
        return [(curr.pk, f"{curr.name} ({curr.symbol})") for curr in currencies]
    except:
        return []


def get_active_currencies():
    """الحصول على العملات النشطة"""
    try:
        return Currency.objects.filter(is_active=True).order_by('name')
    except:
        return []
