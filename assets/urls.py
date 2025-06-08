from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.home, name='home'),
    
    # إدارة الأصول
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('assets/create-ajax/', views.asset_create_ajax, name='asset_create_ajax'),
    path('assets/check-code/', views.check_asset_code, name='check_asset_code'),
    path('assets/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('assets/<int:pk>/edit/', views.asset_edit, name='asset_edit'),
    path('assets/<int:pk>/delete/', views.asset_delete, name='asset_delete'),
    
    # شراء الأصول
    path('purchases/', views.asset_purchase_list, name='asset_purchase_list'),
    path('purchases/create/', views.asset_purchase_create, name='asset_purchase_create'),
    path('purchases/<int:pk>/', views.asset_purchase_detail, name='asset_purchase_detail'),
    path('purchases/<int:pk>/edit/', views.asset_purchase_edit, name='asset_purchase_edit'),
    path('purchases/<int:pk>/delete/', views.asset_purchase_delete, name='asset_purchase_delete'),
    
    # تجديد الأصول
    path('renewals/', views.asset_renewal_list, name='asset_renewal_list'),
    path('renewals/create/', views.asset_renewal_create, name='asset_renewal_create'),
    path('renewals/<int:pk>/', views.asset_renewal_detail, name='asset_renewal_detail'),
    path('renewals/<int:pk>/edit/', views.asset_renewal_edit, name='asset_renewal_edit'),
    path('renewals/<int:pk>/delete/', views.asset_renewal_delete, name='asset_renewal_delete'),
    
    # بيع الأصول
    path('sales/', views.asset_sale_list, name='asset_sale_list'),
    path('sales/create/', views.asset_sale_create, name='asset_sale_create'),
    path('sales/<int:pk>/', views.asset_sale_detail, name='asset_sale_detail'),
    path('sales/<int:pk>/edit/', views.asset_sale_edit, name='asset_sale_edit'),
    path('sales/<int:pk>/delete/', views.asset_sale_delete, name='asset_sale_delete'),
    
    # حساب الإهلاك
    path('depreciation/', views.depreciation_list, name='depreciation_list'),
    path('depreciation/calculate/', views.calculate_depreciation, name='calculate_depreciation'),
    path('depreciation/entries/', views.depreciation_entry_list, name='depreciation_entry_list'),
    path('depreciation/entries/create/', views.depreciation_entry_create, name='depreciation_entry_create'),
    path('depreciation/entries/<int:pk>/', views.depreciation_entry_detail, name='depreciation_entry_detail'),
    path('depreciation/entries/<int:pk>/delete/', views.depreciation_entry_delete, name='depreciation_entry_delete'),
    
    # صيانة الأصول
    path('maintenance/', views.asset_maintenance_list, name='asset_maintenance_list'),
    path('maintenance/create/', views.asset_maintenance_create, name='asset_maintenance_create'),
    path('maintenance/<int:pk>/', views.asset_maintenance_detail, name='asset_maintenance_detail'),
    path('maintenance/<int:pk>/edit/', views.asset_maintenance_edit, name='asset_maintenance_edit'),
    path('maintenance/<int:pk>/delete/', views.asset_maintenance_delete, name='asset_maintenance_delete'),
    
    # تقارير
    path('reports/', views.asset_reports, name='asset_reports'),
    path('reports/asset-register/', views.asset_register_report, name='asset_register_report'),
    path('reports/depreciation-schedule/', views.depreciation_schedule_report, name='depreciation_schedule_report'),
    path('reports/asset-movements/', views.asset_movements_report, name='asset_movements_report'),
]
