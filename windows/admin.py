from django.contrib import admin
from .models import (
    WindowCategory, WindowDefinition, UserWindowPreference,
    OpenWindow, WindowTemplate, QuickAccess
)


@admin.register(WindowCategory)
class WindowCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'icon', 'color', 'order', 'is_active']
    list_filter = ['is_active', 'color']
    search_fields = ['name', 'code']
    ordering = ['order', 'name']


@admin.register(WindowDefinition)
class WindowDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'window_type', 'icon', 'is_active', 'order']
    list_filter = ['category', 'window_type', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['category', 'order', 'name']
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'code', 'category', 'window_type', 'description')
        }),
        ('إعدادات العرض', {
            'fields': ('icon', 'order', 'is_active')
        }),
        ('إعدادات التقنية', {
            'fields': ('url', 'shortcut_key', 'requires_permission')
        }),
    )


@admin.register(UserWindowPreference)
class UserWindowPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'window', 'is_favorite', 'is_pinned', 'usage_count', 'last_used']
    list_filter = ['is_favorite', 'is_pinned', 'window__category']
    search_fields = ['user__username', 'window__name']
    ordering = ['-last_used']


@admin.register(OpenWindow)
class OpenWindowAdmin(admin.ModelAdmin):
    list_display = ['user', 'window', 'title', 'opened_at', 'last_activity', 'is_maximized', 'is_minimized']
    list_filter = ['is_maximized', 'is_minimized', 'window__category']
    search_fields = ['user__username', 'window__name', 'title']
    ordering = ['-last_activity']
    readonly_fields = ['opened_at', 'last_activity']


@admin.register(WindowTemplate)
class WindowTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'window_type', 'default_width', 'default_height', 'is_resizable', 'is_draggable']
    list_filter = ['window_type', 'is_resizable', 'is_draggable']
    search_fields = ['name']
    ordering = ['name']
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'window_type')
        }),
        ('قوالب الكود', {
            'fields': ('html_template', 'css_styles', 'javascript_code'),
            'classes': ('collapse',)
        }),
        ('إعدادات النافذة', {
            'fields': (
                ('default_width', 'default_height'),
                ('is_resizable', 'is_draggable'),
                ('has_close_button', 'has_minimize_button', 'has_maximize_button')
            )
        }),
    )


@admin.register(QuickAccess)
class QuickAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'window', 'position', 'created_at']
    list_filter = ['window__category']
    search_fields = ['user__username', 'window__name']
    ordering = ['user', 'position']
