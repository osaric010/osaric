from .models import TaskbarSettings, LicenseInfo, SystemSettings


def taskbar_settings(request):
    """Context processor لإعدادات شريط المهام"""
    context = {}
    
    if request.user.is_authenticated:
        try:
            settings = TaskbarSettings.objects.get(user=request.user)
            context['user_taskbar_settings'] = settings
        except TaskbarSettings.DoesNotExist:
            context['user_taskbar_settings'] = None
    
    return context


def license_info(request):
    """Context processor لمعلومات الترخيص"""
    context = {}

    try:
        license_obj = LicenseInfo.objects.first()
        context['system_license'] = license_obj
    except LicenseInfo.DoesNotExist:
        context['system_license'] = None

    return context


def ui_settings(request):
    """Context processor لإعدادات الواجهة"""
    try:
        # جلب جميع الإعدادات
        all_settings_dict = {}
        ui_settings_dict = {}

        all_settings_qs = SystemSettings.objects.all()

        for setting in all_settings_qs:
            # تحويل القيم المنطقية
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
            elif setting.value_type == 'FILE':
                value = setting.file_value.url if setting.file_value else None
            else:
                value = setting.value

            all_settings_dict[setting.key] = value

            # إعدادات الواجهة منفصلة
            if setting.category == 'واجهة المستخدم':
                ui_settings_dict[setting.key] = value

        return {
            'ui_settings': ui_settings_dict,
            'system_settings': all_settings_dict
        }
    except Exception:
        # في حالة عدم وجود الجدول أو حدوث خطأ
        return {
            'ui_settings': {
                'ui_theme': 'default',
                'ui_sidebar_collapsed': False,
                'ui_show_tooltips': True,
                'ui_animation_speed': 'normal',
                'ui_records_per_page': 25,
                'ui_primary_color': '#0d6efd',
                'ui_secondary_color': '#6c757d',
                'ui_success_color': '#198754',
                'ui_danger_color': '#dc3545',
                'ui_warning_color': '#ffc107',
                'ui_info_color': '#0dcaf0',
                'ui_font_family': 'Cairo, sans-serif',
                'ui_font_size': 14,
                'ui_border_radius': 8,
                'ui_sidebar_width': 280,
                'ui_header_height': 60,
                'ui_enable_dark_mode': False,
                'ui_enable_rtl': True,
                'ui_enable_animations': True,
                'ui_enable_breadcrumbs': True,
                'ui_enable_notifications': True,
                'ui_table_striped': True,
                'ui_table_hover': True,
                'ui_compact_mode': False,
            }
        }
