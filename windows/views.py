from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, F
import json
from .models import (
    WindowCategory, WindowDefinition, UserWindowPreference,
    OpenWindow, WindowTemplate, QuickAccess
)


@login_required
def windows_dashboard(request):
    """لوحة تحكم النوافذ"""
    # جلب فئات النوافذ مع النوافذ
    categories = WindowCategory.objects.filter(is_active=True).prefetch_related(
        'windowdefinition_set'
    )

    # جلب النوافذ المفضلة للمستخدم
    favorite_windows = UserWindowPreference.objects.filter(
        user=request.user,
        is_favorite=True
    ).select_related('window', 'window__category')

    # جلب النوافذ المفتوحة
    open_windows = OpenWindow.objects.filter(
        user=request.user
    ).select_related('window')

    # جلب الوصول السريع
    quick_access = QuickAccess.objects.filter(
        user=request.user
    ).select_related('window').order_by('position')

    context = {
        'title': 'لوحة تحكم النوافذ',
        'categories': categories,
        'favorite_windows': favorite_windows,
        'open_windows': open_windows,
        'quick_access': quick_access,
    }
    return render(request, 'windows/dashboard.html', context)


@login_required
def open_window(request, window_id):
    """فتح نافذة جديدة"""
    window = get_object_or_404(WindowDefinition, id=window_id, is_active=True)

    # التحقق من الصلاحيات
    if window.requires_permission and not request.user.has_perm(window.requires_permission):
        messages.error(request, 'ليس لديك صلاحية لفتح هذه النافذة')
        return redirect('windows:dashboard')

    # تحديث إحصائيات الاستخدام
    preference, created = UserWindowPreference.objects.get_or_create(
        user=request.user,
        window=window,
        defaults={'usage_count': 0}
    )
    preference.usage_count = F('usage_count') + 1
    preference.last_used = timezone.now()
    preference.save()

    # إنشاء سجل النافذة المفتوحة
    open_window_obj = OpenWindow.objects.create(
        user=request.user,
        window=window,
        session_key=request.session.session_key,
        window_instance_id=f"window_{window.id}_{timezone.now().timestamp()}",
        title=window.name,
        url=window.url or '#',
    )

    context = {
        'window': window,
        'open_window': open_window_obj,
        'title': window.name,
    }

    # إذا كان للنافذة رابط محدد، توجيه إليه
    if window.url:
        return redirect(window.url)

    # وإلا عرض النافذة العامة
    return render(request, 'windows/window_frame.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, window_id):
    """تبديل حالة المفضلة للنافذة"""
    window = get_object_or_404(WindowDefinition, id=window_id)

    preference, created = UserWindowPreference.objects.get_or_create(
        user=request.user,
        window=window,
        defaults={'is_favorite': False}
    )

    preference.is_favorite = not preference.is_favorite
    preference.save()

    return JsonResponse({
        'success': True,
        'is_favorite': preference.is_favorite,
        'message': 'تم إضافة النافذة للمفضلة' if preference.is_favorite else 'تم إزالة النافذة من المفضلة'
    })


@login_required
@require_http_methods(["POST"])
def add_to_quick_access(request, window_id):
    """إضافة نافذة للوصول السريع"""
    window = get_object_or_404(WindowDefinition, id=window_id)

    # التحقق من عدم وجود النافذة في الوصول السريع
    if QuickAccess.objects.filter(user=request.user, window=window).exists():
        return JsonResponse({
            'success': False,
            'message': 'النافذة موجودة بالفعل في الوصول السريع'
        })

    # الحصول على آخر موضع
    last_position = QuickAccess.objects.filter(user=request.user).count()

    QuickAccess.objects.create(
        user=request.user,
        window=window,
        position=last_position
    )

    return JsonResponse({
        'success': True,
        'message': 'تم إضافة النافذة للوصول السريع'
    })


@login_required
@require_http_methods(["POST"])
def remove_from_quick_access(request, window_id):
    """إزالة نافذة من الوصول السريع"""
    window = get_object_or_404(WindowDefinition, id=window_id)

    quick_access = QuickAccess.objects.filter(user=request.user, window=window)
    if quick_access.exists():
        quick_access.delete()
        return JsonResponse({
            'success': True,
            'message': 'تم إزالة النافذة من الوصول السريع'
        })

    return JsonResponse({
        'success': False,
        'message': 'النافذة غير موجودة في الوصول السريع'
    })


@login_required
@require_http_methods(["POST"])
def close_window(request, open_window_id):
    """إغلاق نافذة مفتوحة"""
    open_window = get_object_or_404(OpenWindow, id=open_window_id, user=request.user)
    open_window.delete()

    return JsonResponse({
        'success': True,
        'message': 'تم إغلاق النافذة'
    })


@login_required
@require_http_methods(["POST"])
def update_window_position(request, open_window_id):
    """تحديث موضع وحجم النافذة"""
    open_window = get_object_or_404(OpenWindow, id=open_window_id, user=request.user)

    data = json.loads(request.body)

    if 'x' in data:
        open_window.position_x = data['x']
    if 'y' in data:
        open_window.position_y = data['y']
    if 'width' in data:
        open_window.width = data['width']
    if 'height' in data:
        open_window.height = data['height']
    if 'is_maximized' in data:
        open_window.is_maximized = data['is_maximized']
    if 'is_minimized' in data:
        open_window.is_minimized = data['is_minimized']
    if 'z_index' in data:
        open_window.z_index = data['z_index']

    open_window.last_activity = timezone.now()
    open_window.save()

    return JsonResponse({
        'success': True,
        'message': 'تم تحديث موضع النافذة'
    })


@login_required
def search_windows(request):
    """البحث في النوافذ"""
    query = request.GET.get('q', '')

    if not query:
        return JsonResponse({'windows': []})

    windows = WindowDefinition.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).select_related('category')[:10]

    results = []
    for window in windows:
        results.append({
            'id': window.id,
            'name': window.name,
            'description': window.description or '',
            'category': window.category.name,
            'icon': window.icon,
            'url': window.url or f'/windows/open/{window.id}/'
        })

    return JsonResponse({'windows': results})


@login_required
def calculator(request):
    """آلة حاسبة"""
    context = {
        'title': 'آلة حاسبة',
    }
    return render(request, 'windows/tools/calculator.html', context)


@login_required
def calendar_view(request):
    """تقويم"""
    context = {
        'title': 'التقويم',
    }
    return render(request, 'windows/tools/calendar.html', context)


@login_required
def notepad(request):
    """مفكرة"""
    context = {
        'title': 'المفكرة',
    }
    return render(request, 'windows/tools/notepad.html', context)


@login_required
def task_list(request):
    """قائمة المهام"""
    context = {
        'title': 'قائمة المهام',
    }
    return render(request, 'windows/tools/task_list.html', context)


@login_required
def reminders(request):
    """التذكيرات"""
    context = {
        'title': 'التذكيرات',
    }
    return render(request, 'windows/tools/reminders.html', context)


@login_required
def advanced_search(request):
    """البحث المتقدم"""
    context = {
        'title': 'البحث المتقدم',
    }
    return render(request, 'windows/tools/advanced_search.html', context)
