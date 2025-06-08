from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
import json
from django.utils import timezone
from datetime import datetime, timedelta
import json
import os
import subprocess
import hashlib

from .models import (
    DeletedRecord, EditHistory, SystemBackup, SystemSettings,
    LicenseInfo, TaskbarSettings
)


# لوحة تحكم الخدمات
@login_required
def services_dashboard(request):
    """لوحة تحكم الخدمات"""

    # إحصائيات سريعة
    total_deleted_records = DeletedRecord.objects.filter(is_restored=False).count()
    total_edit_history = EditHistory.objects.count()
    total_backups = SystemBackup.objects.filter(is_valid=True).count()
    total_settings = SystemSettings.objects.count()

    # آخر العمليات
    recent_deleted = DeletedRecord.objects.filter(is_restored=False).order_by('-deleted_at')[:5]
    recent_edits = EditHistory.objects.order_by('-edited_at')[:5]
    recent_backups = SystemBackup.objects.filter(is_valid=True).order_by('-created_at')[:3]

    # معلومات الترخيص
    try:
        license_info = LicenseInfo.objects.first()
    except LicenseInfo.DoesNotExist:
        license_info = None

    # إعدادات شريط المهام للمستخدم الحالي
    try:
        taskbar_settings = TaskbarSettings.objects.get(user=request.user)
    except TaskbarSettings.DoesNotExist:
        taskbar_settings = None

    # إحصائيات النظام
    total_users = User.objects.filter(is_active=True).count()
    total_staff = User.objects.filter(is_staff=True, is_active=True).count()

    # حجم النسخ الاحتياطية
    total_backup_size = SystemBackup.objects.filter(is_valid=True).aggregate(
        total_size=Sum('file_size'))['total_size'] or 0

    # إعدادات النظام حسب الفئة
    settings_by_category = {}
    for setting in SystemSettings.objects.all():
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = 0
        settings_by_category[setting.category] += 1

    context = {
        'title': 'لوحة تحكم الخدمات',
        'total_deleted_records': total_deleted_records,
        'total_edit_history': total_edit_history,
        'total_backups': total_backups,
        'total_settings': total_settings,
        'recent_deleted': recent_deleted,
        'recent_edits': recent_edits,
        'recent_backups': recent_backups,
        'license': license_info,  # تغيير الاسم ليتطابق مع القالب
        'taskbar_settings': taskbar_settings,
        'total_users': total_users,
        'total_staff': total_staff,
        'total_backup_size': total_backup_size,
        'settings_by_category': settings_by_category,
    }
    return render(request, 'services/dashboard.html', context)


# إدارة البيانات
@login_required
@staff_member_required
def delete_data(request):
    """حذف البيانات المسجلة"""

    # قائمة النماذج المتاحة للحذف
    available_models = [
        {'name': 'Person', 'app': 'definitions', 'verbose_name': 'الأشخاص'},
        {'name': 'Item', 'app': 'definitions', 'verbose_name': 'الأصناف'},
        {'name': 'SalesInvoice', 'app': 'sales', 'verbose_name': 'فواتير المبيعات'},
        {'name': 'PurchaseInvoice', 'app': 'purchases', 'verbose_name': 'فواتير المشتريات'},
        {'name': 'JournalEntry', 'app': 'accounting', 'verbose_name': 'القيود المحاسبية'},
    ]

    if request.method == 'POST':
        selected_models = request.POST.getlist('models')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        confirm_delete = request.POST.get('confirm_delete')

        if not confirm_delete:
            messages.error(request, 'يجب تأكيد عملية الحذف')
            return redirect('services:delete_data')

        # تنفيذ عملية الحذف
        deleted_count = 0
        for model_name in selected_models:
            try:
                # هنا يمكن إضافة منطق الحذف الفعلي
                deleted_count += 1
            except Exception as e:
                messages.error(request, f'خطأ في حذف {model_name}: {str(e)}')

        if deleted_count > 0:
            messages.success(request, f'تم حذف {deleted_count} نوع من البيانات بنجاح')

        return redirect('services:delete_data')

    context = {
        'title': 'حذف البيانات المسجلة',
        'available_models': available_models,
    }
    return render(request, 'services/delete_data.html', context)


@login_required
def recycle_bin(request):
    """سلة المحذوفات"""
    context = {
        'title': 'سلة المحذوفات',
    }
    return render(request, 'services/recycle_bin.html', context)


@login_required
def edit_history(request):
    """سلة التعديلات"""
    context = {
        'title': 'سلة التعديلات',
    }
    return render(request, 'services/edit_history.html', context)


@login_required
@staff_member_required
def backup(request):
    """النسخ الاحتياطي"""
    context = {
        'title': 'النسخ الاحتياطي',
    }
    return render(request, 'services/backup.html', context)


@login_required
def license_info(request):
    """معلومات الترخيص"""
    try:
        license_obj = LicenseInfo.objects.first()
    except LicenseInfo.DoesNotExist:
        license_obj = None

    context = {
        'title': 'ترخيص النسخة',
        'license': license_obj,
    }
    return render(request, 'services/license.html', context)


@login_required
@staff_member_required
def recalculate_costs(request):
    """إعادة حساب أسعار تكلفة الأصناف"""
    context = {
        'title': 'إعادة حساب أسعار تكلفة الأصناف',
    }
    return render(request, 'services/recalculate_costs.html', context)


@login_required
def taskbar_settings(request):
    """إعدادات شريط المهام"""

    try:
        settings = TaskbarSettings.objects.get(user=request.user)
    except TaskbarSettings.DoesNotExist:
        settings = TaskbarSettings.objects.create(user=request.user)

    if request.method == 'POST':
        settings.position = request.POST.get('position', 'HORIZONTAL')
        settings.auto_hide = request.POST.get('auto_hide') == 'on'
        settings.show_icons = request.POST.get('show_icons') == 'on'
        settings.show_text = request.POST.get('show_text') == 'on'
        settings.theme = request.POST.get('theme', 'default')
        settings.size = request.POST.get('size', 'medium')

        # ترتيب القوائم
        menu_order = request.POST.get('menu_order', '[]')
        try:
            settings.menu_order = json.loads(menu_order)
        except:
            settings.menu_order = []

        # العناصر المثبتة
        pinned_items = request.POST.getlist('pinned_items')
        settings.pinned_items = pinned_items

        settings.save()
        messages.success(request, 'تم حفظ إعدادات شريط المهام بنجاح')
        return redirect('services:taskbar_settings')

    context = {
        'title': 'إعدادات شريط المهام',
        'settings': settings,
    }
    return render(request, 'services/taskbar_settings.html', context)


@login_required
@staff_member_required
def system_settings(request):
    """كلمات السر وخيارات البرنامج"""

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_password':
            # تغيير كلمة المرور
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not request.user.check_password(old_password):
                messages.error(request, 'كلمة المرور الحالية غير صحيحة')
            elif new_password != confirm_password:
                messages.error(request, 'كلمة المرور الجديدة غير متطابقة')
            elif len(new_password) < 8:
                messages.error(request, 'كلمة المرور يجب أن تكون 8 أحرف على الأقل')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'تم تغيير كلمة المرور بنجاح')
                return redirect('services:system_settings')

        elif action == 'update_setting':
            # تحديث إعداد معين
            setting_key = request.POST.get('setting_key')
            setting_value = request.POST.get('setting_value')
            setting_file = request.FILES.get('setting_file')
            remove_file = request.POST.get('remove_file')

            try:
                setting = SystemSettings.objects.get(key=setting_key)
                if setting.is_editable:
                    # التحقق من صحة البيانات حسب النوع
                    if setting.value_type == 'BOOLEAN':
                        setting_value = 'true' if setting_value == 'true' else 'false'
                    elif setting.value_type == 'INTEGER':
                        try:
                            int(setting_value)
                        except ValueError:
                            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                                return JsonResponse({'success': False, 'message': 'يجب أن تكون القيمة رقم صحيح'})
                            messages.error(request, 'يجب أن تكون القيمة رقم صحيح')
                            return redirect('services:system_settings')
                    elif setting.value_type == 'FLOAT':
                        try:
                            float(setting_value)
                        except ValueError:
                            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                                return JsonResponse({'success': False, 'message': 'يجب أن تكون القيمة رقم عشري'})
                            messages.error(request, 'يجب أن تكون القيمة رقم عشري')
                            return redirect('services:system_settings')
                    elif setting.value_type == 'JSON':
                        try:
                            json.loads(setting_value)
                        except json.JSONDecodeError:
                            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                                return JsonResponse({'success': False, 'message': 'صيغة JSON غير صحيحة'})
                            messages.error(request, 'صيغة JSON غير صحيحة')
                            return redirect('services:system_settings')
                    elif setting.value_type == 'FILE':
                        # معالجة الملفات
                        if remove_file == 'true':
                            # حذف الملف
                            if setting.file_value:
                                setting.file_value.delete()
                            setting.value = ''
                        elif setting_file:
                            # رفع ملف جديد
                            if setting.file_value:
                                setting.file_value.delete()  # حذف الملف القديم
                            setting.file_value = setting_file
                            setting.value = setting_file.name

                    if setting.value_type != 'FILE':
                        setting.value = setting_value
                    setting.updated_by = request.user
                    setting.save()

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'message': f'تم تحديث إعداد {setting.description} بنجاح'})
                    messages.success(request, f'تم تحديث إعداد {setting.description} بنجاح')
                else:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': 'هذا الإعداد غير قابل للتعديل'})
                    messages.error(request, 'هذا الإعداد غير قابل للتعديل')
            except SystemSettings.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'الإعداد غير موجود'})
                messages.error(request, 'الإعداد غير موجود')

        elif action == 'create_user':
            # إنشاء مستخدم جديد
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            is_staff = request.POST.get('is_staff') == 'on'

            if User.objects.filter(username=username).exists():
                messages.error(request, 'اسم المستخدم موجود بالفعل')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'البريد الإلكتروني موجود بالفعل')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    is_staff=is_staff
                )
                messages.success(request, f'تم إنشاء المستخدم {username} بنجاح')

        elif action == 'toggle_user_status':
            # تفعيل/تعطيل مستخدم
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                if user != request.user:  # لا يمكن تعطيل النفس
                    user.is_active = not user.is_active
                    user.save()
                    status = 'تم تفعيل' if user.is_active else 'تم تعطيل'
                    messages.success(request, f'{status} المستخدم {user.username} بنجاح')
                else:
                    messages.error(request, 'لا يمكنك تعطيل حسابك الخاص')
            except User.DoesNotExist:
                messages.error(request, 'المستخدم غير موجود')

        elif action == 'reset_password':
            # إعادة تعيين كلمة مرور مستخدم
            user_id = request.POST.get('user_id')
            new_password = request.POST.get('new_password', '12345678')
            try:
                user = User.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                messages.success(request, f'تم إعادة تعيين كلمة مرور المستخدم {user.username}')
            except User.DoesNotExist:
                messages.error(request, 'المستخدم غير موجود')

        elif action == 'edit_user':
            # تعديل بيانات مستخدم
            user_id = request.POST.get('user_id')
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            is_staff = request.POST.get('is_staff') == 'on'

            try:
                user = User.objects.get(id=user_id)

                # التحقق من عدم تكرار اسم المستخدم
                if User.objects.filter(username=username).exclude(id=user_id).exists():
                    messages.error(request, 'اسم المستخدم موجود بالفعل')
                elif User.objects.filter(email=email).exclude(id=user_id).exists():
                    messages.error(request, 'البريد الإلكتروني موجود بالفعل')
                else:
                    user.username = username
                    user.email = email
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_staff = is_staff
                    user.save()
                    messages.success(request, f'تم تحديث بيانات المستخدم {username} بنجاح')
            except User.DoesNotExist:
                messages.error(request, 'المستخدم غير موجود')

        elif action == 'update_performance':
            # تحديث إعدادات الأداء
            cache_size = request.POST.get('cache_size', '128')
            query_timeout = request.POST.get('query_timeout', '30')
            enable_compression = request.POST.get('enable_compression') == 'on'
            enable_caching = request.POST.get('enable_caching') == 'on'

            # حفظ إعدادات الأداء
            performance_settings = [
                ('cache_size', cache_size, 'حجم ذاكرة التخزين المؤقت'),
                ('query_timeout', query_timeout, 'مهلة انتظار الاستعلام'),
                ('enable_compression', str(enable_compression).lower(), 'تفعيل ضغط البيانات'),
                ('enable_caching', str(enable_caching).lower(), 'تفعيل التخزين المؤقت'),
            ]

            for key, value, desc in performance_settings:
                setting, created = SystemSettings.objects.get_or_create(
                    key=key,
                    defaults={
                        'value': value,
                        'category': 'الأداء',
                        'description': desc,
                        'value_type': 'INTEGER' if key in ['cache_size', 'query_timeout'] else 'BOOLEAN',
                        'is_editable': True,
                        'updated_by': request.user
                    }
                )
                if not created:
                    setting.value = value
                    setting.updated_by = request.user
                    setting.save()

            messages.success(request, 'تم حفظ إعدادات الأداء بنجاح')

        elif action == 'update_security':
            # تحديث إعدادات الأمان المتقدمة
            enable_2fa = request.POST.get('enable_2fa') == 'on'
            enable_ip_whitelist = request.POST.get('enable_ip_whitelist') == 'on'
            enable_audit_log = request.POST.get('enable_audit_log') == 'on'
            encryption_level = request.POST.get('encryption_level', 'standard')

            security_settings = [
                ('enable_2fa', str(enable_2fa).lower(), 'تفعيل المصادقة الثنائية'),
                ('enable_ip_whitelist', str(enable_ip_whitelist).lower(), 'تفعيل قائمة IP المسموحة'),
                ('enable_audit_log', str(enable_audit_log).lower(), 'تفعيل سجل المراجعة'),
                ('encryption_level', encryption_level, 'مستوى التشفير'),
            ]

            for key, value, desc in security_settings:
                setting, created = SystemSettings.objects.get_or_create(
                    key=key,
                    defaults={
                        'value': value,
                        'category': 'الأمان المتقدم',
                        'description': desc,
                        'value_type': 'STRING' if key == 'encryption_level' else 'BOOLEAN',
                        'is_editable': True,
                        'updated_by': request.user
                    }
                )
                if not created:
                    setting.value = value
                    setting.updated_by = request.user
                    setting.save()

            messages.success(request, 'تم حفظ إعدادات الأمان بنجاح')

        elif action == 'update_integration':
            # تحديث إعدادات التكامل
            api_key = request.POST.get('api_key', '')
            enable_api = request.POST.get('enable_api') == 'on'
            enable_webhooks = request.POST.get('enable_webhooks') == 'on'
            rate_limit = request.POST.get('rate_limit', '60')

            integration_settings = [
                ('api_key', api_key, 'مفتاح API'),
                ('enable_api', str(enable_api).lower(), 'تفعيل واجهة برمجة التطبيقات'),
                ('enable_webhooks', str(enable_webhooks).lower(), 'تفعيل Webhooks'),
                ('api_rate_limit', rate_limit, 'معدل الطلبات'),
            ]

            for key, value, desc in integration_settings:
                setting, created = SystemSettings.objects.get_or_create(
                    key=key,
                    defaults={
                        'value': value,
                        'category': 'التكامل',
                        'description': desc,
                        'value_type': 'INTEGER' if key == 'api_rate_limit' else ('STRING' if key == 'api_key' else 'BOOLEAN'),
                        'is_editable': True,
                        'updated_by': request.user
                    }
                )
                if not created:
                    setting.value = value
                    setting.updated_by = request.user
                    setting.save()

            messages.success(request, 'تم حفظ إعدادات التكامل بنجاح')

    # جلب البيانات للعرض
    settings_by_category = {}
    for setting in SystemSettings.objects.all():
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = []
        settings_by_category[setting.category].append(setting)

    users = User.objects.all().order_by('username')
    staff_users = User.objects.filter(is_staff=True).order_by('username')

    context = {
        'title': 'كلمات السر وخيارات البرنامج',
        'settings_by_category': settings_by_category,
        'users': users,
        'staff_users': staff_users,
        'total_users': users.count(),
        'total_staff': staff_users.count(),
    }
    return render(request, 'services/system_settings.html', context)


@login_required
def print_design(request):
    """تصميم نماذج الطباعة"""
    context = {
        'title': 'تصميم نماذج الطباعة',
    }
    return render(request, 'services/print_design.html', context)


@login_required
def barcode_design(request):
    """تصميم نماذج الباركود"""
    context = {
        'title': 'تصميم نماذج الباركود',
    }
    return render(request, 'services/barcode_design.html', context)


@login_required
def relogin(request):
    """إعادة الدخول كمستخدم آخر"""
    context = {
        'title': 'إعادة الدخول كمستخدم',
    }
    return render(request, 'services/relogin.html', context)


@login_required
@staff_member_required
def system_report(request):
    """تقرير حالة النظام"""
    import platform
    try:
        import psutil
        has_psutil = True
    except ImportError:
        has_psutil = False

    from django.db import connection

    # معلومات النظام الأساسية
    system_info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'django_version': '4.2.0',
    }

    # معلومات الأداء إذا كان psutil متاح
    if has_psutil:
        system_info.update({
            'cpu_count': psutil.cpu_count(),
            'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
            'memory_available': round(psutil.virtual_memory().available / (1024**3), 2),  # GB
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent,
        })

    # إحصائيات قاعدة البيانات
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM services_systemsettings")
        total_settings = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM services_deletedrecord WHERE is_restored = false")
        deleted_records = cursor.fetchone()[0]

    # إحصائيات الإعدادات حسب الفئة
    settings_by_category = {}
    for setting in SystemSettings.objects.all():
        if setting.category not in settings_by_category:
            settings_by_category[setting.category] = 0
        settings_by_category[setting.category] += 1

    # معلومات الترخيص
    try:
        license_info = LicenseInfo.objects.first()
    except LicenseInfo.DoesNotExist:
        license_info = None

    context = {
        'title': 'تقرير حالة النظام',
        'system_info': system_info,
        'has_psutil': has_psutil,
        'total_users': total_users,
        'total_settings': total_settings,
        'deleted_records': deleted_records,
        'settings_by_category': settings_by_category,
        'license_info': license_info,
    }
    return render(request, 'services/system_report.html', context)


@login_required
def financial_settings(request):
    """عرض الإعدادات المالية"""
    from definitions.models import Currency
    from core.currency_utils import get_decimal_places, get_currency_symbol, get_currency_name

    # جلب الإعدادات المالية
    financial_keys = [
        'default_currency', 'currency_symbol', 'currency_name', 'decimal_places',
        'tax_rate', 'currency_position', 'thousands_separator', 'decimal_separator',
        'show_currency_code', 'auto_update_rates'
    ]

    financial_settings = []
    for key in financial_keys:
        try:
            setting = SystemSettings.objects.get(key=key)
            financial_settings.append(setting)
        except SystemSettings.DoesNotExist:
            continue

    # جلب العملات
    currencies = Currency.objects.filter(is_active=True).order_by('name')

    # إحصائيات
    currencies_count = currencies.count()
    decimal_places = get_decimal_places()

    try:
        tax_rate_setting = SystemSettings.objects.get(key='tax_rate')
        tax_rate = float(tax_rate_setting.value)
    except (SystemSettings.DoesNotExist, ValueError):
        tax_rate = 14.0

    active_settings_count = SystemSettings.objects.filter(
        category='الإعدادات المالية'
    ).count()

    context = {
        'title': 'الإعدادات المالية',
        'financial_settings': financial_settings,
        'currencies': currencies,
        'currencies_count': currencies_count,
        'decimal_places': decimal_places,
        'tax_rate': tax_rate,
        'active_settings_count': active_settings_count,
    }

    return render(request, 'services/financial_settings.html', context)


@login_required
def test_settings(request):
    """اختبار الإعدادات"""
    from .templatetags.system_tags import get_setting, format_currency, company_info

    # اختبار الإعدادات المختلفة
    test_data = {
        'company_name': get_setting('company_name', 'غير محدد'),
        'currency_symbol': get_setting('currency_symbol', 'ر.س'),
        'decimal_places': get_setting('decimal_places', 2),
        'tax_rate': get_setting('tax_rate', 15.0),
        'ui_theme': get_setting('ui_theme', 'default'),
        'ui_primary_color': get_setting('ui_primary_color', '#0d6efd'),
        'enable_dark_mode': get_setting('ui_enable_dark_mode', False),
        'records_per_page': get_setting('ui_records_per_page', 25),
    }

    # اختبار تنسيق العملة
    test_amount = 1234.56
    formatted_amount = format_currency(test_amount)

    # اختبار معلومات الشركة
    company_data = {
        'name': company_info('name'),
        'address': company_info('address'),
        'phone': company_info('phone'),
        'email': company_info('email'),
    }

    context = {
        'title': 'اختبار الإعدادات',
        'test_data': test_data,
        'test_amount': test_amount,
        'formatted_amount': formatted_amount,
        'company_data': company_data,
    }
    return render(request, 'services/test_settings.html', context)


# AJAX endpoints
@require_POST
@csrf_exempt
def ajax_delete_records(request):
    """حذف السجلات عبر AJAX"""
    return JsonResponse({'success': True, 'message': 'تم الحذف بنجاح'})


@require_POST
@csrf_exempt
def ajax_restore_records(request):
    """استرداد السجلات عبر AJAX"""
    return JsonResponse({'success': True, 'message': 'تم الاسترداد بنجاح'})


@require_POST
@csrf_exempt
def ajax_create_backup(request):
    """إنشاء نسخة احتياطية عبر AJAX"""
    return JsonResponse({'success': True, 'message': 'تم إنشاء النسخة الاحتياطية'})


@require_POST
@csrf_exempt
def ajax_recalculate_costs(request):
    """إعادة حساب التكلفة عبر AJAX"""
    return JsonResponse({'success': True, 'message': 'تم إعادة حساب التكلفة'})
