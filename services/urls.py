from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # لوحة تحكم الخدمات
    path('', views.services_dashboard, name='services_dashboard'),

    # إدارة البيانات
    path('delete-data/', views.delete_data, name='delete_data'),
    path('recycle-bin/', views.recycle_bin, name='recycle_bin'),
    path('edit-history/', views.edit_history, name='edit_history'),
    
    # النسخ الاحتياطي والترخيص
    path('backup/', views.backup, name='backup'),
    path('license/', views.license_info, name='license'),
    
    # أدوات النظام
    path('recalculate-costs/', views.recalculate_costs, name='recalculate_costs'),
    path('taskbar-settings/', views.taskbar_settings, name='taskbar_settings'),
    
    # الإعدادات والأمان
    path('system-settings/', views.system_settings, name='system_settings'),
    path('financial-settings/', views.financial_settings, name='financial_settings'),
    path('print-design/', views.print_design, name='print_design'),
    path('barcode-design/', views.barcode_design, name='barcode_design'),
    path('relogin/', views.relogin, name='relogin'),

    # تقرير حالة النظام
    path('system-report/', views.system_report, name='system_report'),

    # اختبار الإعدادات
    path('test-settings/', views.test_settings, name='test_settings'),

    # AJAX endpoints
    path('ajax/delete-records/', views.ajax_delete_records, name='ajax_delete_records'),
    path('ajax/restore-records/', views.ajax_restore_records, name='ajax_restore_records'),
    path('ajax/backup-create/', views.ajax_create_backup, name='ajax_create_backup'),
    path('ajax/recalculate/', views.ajax_recalculate_costs, name='ajax_recalculate'),
]
