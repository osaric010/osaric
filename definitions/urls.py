from django.urls import path
from . import views

app_name = 'definitions'

urlpatterns = [
    # الصفحة الرئيسية للتعريفات
    path('', views.definitions_home, name='home'),
    
    # العملات
    path('currencies/', views.currency_list, name='currency_list'),
    path('currencies/create/', views.currency_create, name='currency_create'),
    path('currencies/<int:pk>/edit/', views.currency_edit, name='currency_edit'),
    path('currencies/<int:pk>/delete/', views.currency_delete, name='currency_delete'),
    
    # المخازن
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/edit/', views.warehouse_edit, name='warehouse_edit'),
    path('warehouses/<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),
    
    # فئات الأصناف
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # وحدات القياس
    path('units/', views.unit_list, name='unit_list'),
    path('units/create/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/edit/', views.unit_edit, name='unit_edit'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),
    
    # الأصناف
    path('items/', views.item_list, name='item_list'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:pk>/delete/', views.item_delete, name='item_delete'),
    
    # البنوك
    path('banks/', views.bank_list, name='bank_list'),
    path('banks/create/', views.bank_create, name='bank_create'),
    path('banks/<int:pk>/edit/', views.bank_edit, name='bank_edit'),
    path('banks/<int:pk>/delete/', views.bank_delete, name='bank_delete'),
    
    # الخزائن
    path('treasuries/', views.treasury_list, name='treasury_list'),
    path('treasuries/create/', views.treasury_create, name='treasury_create'),
    path('treasuries/<int:pk>/edit/', views.treasury_edit, name='treasury_edit'),
    path('treasuries/<int:pk>/delete/', views.treasury_delete, name='treasury_delete'),

    # مناطق المخازن
    path('zones/', views.zone_list, name='zone_list'),
    path('zones/create/', views.zone_create, name='zone_create'),
    path('zones/<int:pk>/edit/', views.zone_edit, name='zone_edit'),
    path('zones/<int:pk>/delete/', views.zone_delete, name='zone_delete'),

    # مواقع المخازن
    path('locations/', views.location_list, name='location_list'),
    path('locations/create/', views.location_create, name='location_create'),
    path('locations/<int:pk>/edit/', views.location_edit, name='location_edit'),
    path('locations/<int:pk>/delete/', views.location_delete, name='location_delete'),

    # مواقع الأصناف
    path('item-locations/', views.item_location_list, name='item_location_list'),
    path('item-locations/create/', views.item_location_create, name='item_location_create'),
    path('item-locations/<int:pk>/edit/', views.item_location_edit, name='item_location_edit'),
    path('item-locations/<int:pk>/delete/', views.item_location_delete, name='item_location_delete'),

    # مجموعات الأصول
    path('asset-groups/', views.asset_group_list, name='asset_group_list'),
    path('asset-groups/create/', views.asset_group_create, name='asset_group_create'),
    path('asset-groups/<int:pk>/edit/', views.asset_group_edit, name='asset_group_edit'),
    path('asset-groups/<int:pk>/delete/', views.asset_group_delete, name='asset_group_delete'),

    # الأشخاص والجهات
    path('persons/', views.person_list, name='person_list'),
    path('persons/create/', views.person_create, name='person_create'),
    path('persons/<int:pk>/', views.person_detail, name='person_detail'),
    path('persons/<int:pk>/edit/', views.person_edit, name='person_edit'),
    path('persons/<int:pk>/delete/', views.person_delete, name='person_delete'),

    # فئات المصروفات
    path('expense-categories/', views.expense_category_list, name='expense_category_list'),
    path('expense-categories/create/', views.expense_category_create, name='expense_category_create'),
    path('expense-categories/<int:pk>/edit/', views.expense_category_edit, name='expense_category_edit'),
    path('expense-categories/<int:pk>/delete/', views.expense_category_delete, name='expense_category_delete'),

    # بنود المصروفات
    path('expense-items/', views.expense_item_list, name='expense_item_list'),
    path('expense-items/create/', views.expense_item_create, name='expense_item_create'),
    path('expense-items/<int:pk>/edit/', views.expense_item_edit, name='expense_item_edit'),
    path('expense-items/<int:pk>/delete/', views.expense_item_delete, name='expense_item_delete'),

    # فئات الإيرادات
    path('revenue-categories/', views.revenue_category_list, name='revenue_category_list'),
    path('revenue-categories/create/', views.revenue_category_create, name='revenue_category_create'),
    path('revenue-categories/<int:pk>/edit/', views.revenue_category_edit, name='revenue_category_edit'),
    path('revenue-categories/<int:pk>/delete/', views.revenue_category_delete, name='revenue_category_delete'),

    # بنود الإيرادات
    path('revenue-items/', views.revenue_item_list, name='revenue_item_list'),
    path('revenue-items/create/', views.revenue_item_create, name='revenue_item_create'),
    path('revenue-items/<int:pk>/edit/', views.revenue_item_edit, name='revenue_item_edit'),
    path('revenue-items/<int:pk>/delete/', views.revenue_item_delete, name='revenue_item_delete'),

    # مراحل الإنتاج
    path('production-stages/', views.production_stage_list, name='production_stage_list'),
    path('production-stages/create/', views.production_stage_create, name='production_stage_create'),
    path('production-stages/<int:pk>/', views.production_stage_detail, name='production_stage_detail'),
    path('production-stages/<int:pk>/edit/', views.production_stage_edit, name='production_stage_edit'),
    path('production-stages/<int:pk>/delete/', views.production_stage_delete, name='production_stage_delete'),

    # المنتجات التامة
    path('finished-products/', views.finished_product_list, name='finished_product_list'),
    path('finished-products/create/', views.finished_product_create, name='finished_product_create'),
    path('finished-products/<int:pk>/', views.finished_product_detail, name='finished_product_detail'),
    path('finished-products/<int:pk>/edit/', views.finished_product_edit, name='finished_product_edit'),
    path('finished-products/<int:pk>/delete/', views.finished_product_delete, name='finished_product_delete'),

    # مراكز الربحية
    path('profit-centers/', views.profit_center_list, name='profit_center_list'),
    path('profit-centers/create/', views.profit_center_create, name='profit_center_create'),
    path('profit-centers/<int:pk>/', views.profit_center_detail, name='profit_center_detail'),
    path('profit-centers/<int:pk>/edit/', views.profit_center_edit, name='profit_center_edit'),
    path('profit-centers/<int:pk>/delete/', views.profit_center_delete, name='profit_center_delete'),

    # الطابعات
    path('printers/', views.printer_list, name='printer_list'),
    path('printers/create/', views.printer_create, name='printer_create'),
    path('printers/<int:pk>/', views.printer_detail, name='printer_detail'),
    path('printers/<int:pk>/edit/', views.printer_edit, name='printer_edit'),
    path('printers/<int:pk>/delete/', views.printer_delete, name='printer_delete'),

    # إعدادات الشركة
    path('company-settings/', views.company_settings, name='company_settings'),
    path('upload-logo/', views.upload_logo, name='upload_logo'),
    path('remove-logo/', views.remove_logo, name='remove_logo'),
    path('company-info/', views.get_company_info, name='get_company_info'),
]
