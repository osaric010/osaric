from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # لوحة التحكم
    path('', views.dashboard, name='dashboard'),
    
    # أنظمة صرف المرتبات
    path('salary-systems/', views.salary_system_list, name='salary_system_list'),
    path('salary-systems/create/', views.salary_system_create, name='salary_system_create'),
    path('salary-systems/<int:pk>/', views.salary_system_detail, name='salary_system_detail'),
    path('salary-systems/<int:pk>/edit/', views.salary_system_edit, name='salary_system_edit'),
    path('salary-systems/<int:pk>/delete/', views.salary_system_delete, name='salary_system_delete'),
    
    # الأقسام
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    # المناصب
    path('positions/', views.position_list, name='position_list'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/', views.position_detail, name='position_detail'),
    path('positions/<int:pk>/edit/', views.position_edit, name='position_edit'),
    path('positions/<int:pk>/delete/', views.position_delete, name='position_delete'),
    
    # الموظفين
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
]
