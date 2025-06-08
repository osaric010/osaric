from django.urls import path
from . import views

app_name = 'windows'

urlpatterns = [
    # لوحة تحكم النوافذ
    path('', views.windows_dashboard, name='dashboard'),
    
    # إدارة النوافذ
    path('open/<int:window_id>/', views.open_window, name='open_window'),
    path('close/<int:open_window_id>/', views.close_window, name='close_window'),
    path('update-position/<int:open_window_id>/', views.update_window_position, name='update_window_position'),
    
    # المفضلة والوصول السريع
    path('toggle-favorite/<int:window_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('add-quick-access/<int:window_id>/', views.add_to_quick_access, name='add_to_quick_access'),
    path('remove-quick-access/<int:window_id>/', views.remove_from_quick_access, name='remove_from_quick_access'),
    
    # البحث
    path('search/', views.search_windows, name='search_windows'),
    
    # الأدوات المتنوعة
    path('tools/calculator/', views.calculator, name='calculator'),
    path('tools/calendar/', views.calendar_view, name='calendar'),
    path('tools/notepad/', views.notepad, name='notepad'),
    path('tools/task-list/', views.task_list, name='task_list'),
    path('tools/reminders/', views.reminders, name='reminders'),
    path('tools/advanced-search/', views.advanced_search, name='advanced_search'),
]
