"""
Template tags for date and time formatting
"""

from django import template
from django.utils import timezone
from django.utils.dateformat import format
import datetime

register = template.Library()


@register.filter
def arabic_date(value):
    """تنسيق التاريخ بالعربية"""
    if not value:
        return ''
    
    if isinstance(value, str):
        return value
    
    # تحويل إلى المنطقة الزمنية المحلية
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    
    # تنسيق التاريخ
    return format(value, 'Y-m-d')


@register.filter
def arabic_datetime(value):
    """تنسيق التاريخ والوقت بالعربية مع تنسيق 12 ساعة"""
    if not value:
        return ''
    
    if isinstance(value, str):
        return value
    
    # تحويل إلى المنطقة الزمنية المحلية
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    
    # تنسيق التاريخ والوقت بتنسيق 12 ساعة
    return format(value, 'Y-m-d h:i A')


@register.filter
def arabic_time(value):
    """تنسيق الوقت بالعربية مع تنسيق 12 ساعة"""
    if not value:
        return ''
    
    if isinstance(value, str):
        return value
    
    # تحويل إلى المنطقة الزمنية المحلية
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    
    # تنسيق الوقت بتنسيق 12 ساعة
    return format(value, 'h:i A')


@register.filter
def arabic_datetime_short(value):
    """تنسيق مختصر للتاريخ والوقت"""
    if not value:
        return ''
    
    if isinstance(value, str):
        return value
    
    # تحويل إلى المنطقة الزمنية المحلية
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    
    # تنسيق مختصر
    return format(value, 'm/d h:i A')


@register.filter
def format_datetime_custom(value, format_string='Y-m-d h:i A'):
    """تنسيق مخصص للتاريخ والوقت"""
    if not value:
        return ''
    
    if isinstance(value, str):
        return value
    
    # تحويل إلى المنطقة الزمنية المحلية
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    
    return format(value, format_string)


@register.filter
def time_since_arabic(value):
    """حساب الوقت المنقضي بالعربية"""
    if not value:
        return ''
    
    now = timezone.now()
    if timezone.is_aware(value):
        value = timezone.localtime(value)
        now = timezone.localtime(now)
    
    diff = now - value
    
    if diff.days > 0:
        if diff.days == 1:
            return 'منذ يوم واحد'
        elif diff.days < 11:
            return f'منذ {diff.days} أيام'
        else:
            return arabic_date(value)
    
    hours = diff.seconds // 3600
    if hours > 0:
        if hours == 1:
            return 'منذ ساعة واحدة'
        elif hours < 11:
            return f'منذ {hours} ساعات'
        else:
            return f'منذ {hours} ساعة'
    
    minutes = (diff.seconds % 3600) // 60
    if minutes > 0:
        if minutes == 1:
            return 'منذ دقيقة واحدة'
        elif minutes < 11:
            return f'منذ {minutes} دقائق'
        else:
            return f'منذ {minutes} دقيقة'
    
    return 'منذ لحظات'


@register.filter
def is_today(value):
    """التحقق من أن التاريخ هو اليوم"""
    if not value:
        return False
    
    today = timezone.now().date()
    if hasattr(value, 'date'):
        value = value.date()
    
    return value == today


@register.filter
def is_this_week(value):
    """التحقق من أن التاريخ في هذا الأسبوع"""
    if not value:
        return False
    
    today = timezone.now().date()
    if hasattr(value, 'date'):
        value = value.date()
    
    # حساب بداية الأسبوع (السبت في التقويم العربي)
    days_since_saturday = (today.weekday() + 2) % 7
    week_start = today - datetime.timedelta(days=days_since_saturday)
    week_end = week_start + datetime.timedelta(days=6)
    
    return week_start <= value <= week_end


@register.filter
def is_this_month(value):
    """التحقق من أن التاريخ في هذا الشهر"""
    if not value:
        return False
    
    today = timezone.now().date()
    if hasattr(value, 'date'):
        value = value.date()
    
    return value.year == today.year and value.month == today.month


@register.filter
def weekday_arabic(value):
    """اسم اليوم بالعربية"""
    if not value:
        return ''
    
    if hasattr(value, 'date'):
        value = value.date()
    
    weekdays = {
        0: 'الاثنين',
        1: 'الثلاثاء', 
        2: 'الأربعاء',
        3: 'الخميس',
        4: 'الجمعة',
        5: 'السبت',
        6: 'الأحد'
    }
    
    return weekdays.get(value.weekday(), '')


@register.filter
def month_arabic(value):
    """اسم الشهر بالعربية"""
    if not value:
        return ''
    
    if hasattr(value, 'date'):
        value = value.date()
    
    months = {
        1: 'يناير',
        2: 'فبراير',
        3: 'مارس',
        4: 'أبريل',
        5: 'مايو',
        6: 'يونيو',
        7: 'يوليو',
        8: 'أغسطس',
        9: 'سبتمبر',
        10: 'أكتوبر',
        11: 'نوفمبر',
        12: 'ديسمبر'
    }
    
    return months.get(value.month, '')


@register.simple_tag
def current_time():
    """الوقت الحالي"""
    return timezone.now()


@register.simple_tag
def current_date():
    """التاريخ الحالي"""
    return timezone.now().date()


@register.simple_tag
def cairo_time():
    """وقت القاهرة"""
    cairo_tz = timezone.get_fixed_timezone(120)  # UTC+2
    return timezone.now().astimezone(cairo_tz)
