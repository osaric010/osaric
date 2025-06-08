from django.urls import path
from . import views, opening_views

app_name = 'accounting'

urlpatterns = [
    # لوحة تحكم الحسابات العامة
    path('', views.accounting_dashboard, name='accounting_dashboard'),

    # تحويل رصيد بين الأشخاص
    path('balance-transfer/', views.balance_transfer, name='balance_transfer'),
    path('balance-transfer/add/', views.balance_transfer_add, name='balance_transfer_add'),
    path('balance-transfer/<int:pk>/edit/', views.balance_transfer_edit, name='balance_transfer_edit'),
    path('balance-transfer/<int:pk>/delete/', views.balance_transfer_delete, name='balance_transfer_delete'),
    
    # دمج الحسابات الفرعية
    path('merge-accounts/', views.merge_accounts, name='merge_accounts'),
    path('merge-accounts/add/', views.merge_accounts_add, name='merge_accounts_add'),
    path('merge-accounts/<int:pk>/edit/', views.merge_accounts_edit, name='merge_accounts_edit'),
    path('merge-accounts/<int:pk>/delete/', views.merge_accounts_delete, name='merge_accounts_delete'),
    
    # القيود المحاسبية
    path('journal-entries/', views.journal_entries, name='journal_entries'),
    path('journal-entries/add/', views.journal_entry_add, name='journal_entry_add'),
    path('journal-entries/<int:pk>/edit/', views.journal_entry_edit, name='journal_entry_edit'),
    path('journal-entries/<int:pk>/delete/', views.journal_entry_delete, name='journal_entry_delete'),
    path('journal-entries/<int:pk>/post/', views.journal_entry_post, name='journal_entry_post'),
    
    # القيد الافتتاحي
    path('opening-balance/', views.opening_balance, name='opening_balance'),
    path('opening-balance/setup/', views.opening_balance_setup, name='opening_balance_setup'),
    path('opening-balance/add/', views.opening_balance_add, name='opening_balance_add'),
    path('opening-balance/<int:pk>/edit/', views.opening_balance_edit, name='opening_balance_edit'),
    path('opening-balance/<int:pk>/delete/', views.opening_balance_delete, name='opening_balance_delete'),

    # جرد بضاعة أول المدة (ضمن القيد الافتتاحي)
    path('opening-inventory/', opening_views.opening_inventory_list, name='opening_inventory_list'),
    path('opening-inventory/create/', opening_views.opening_inventory_create, name='opening_inventory_create'),
    path('opening-inventory/<int:pk>/', opening_views.opening_inventory_detail, name='opening_inventory_detail'),
    path('opening-inventory/<int:pk>/edit/', opening_views.opening_inventory_edit, name='opening_inventory_edit'),
    path('opening-inventory/<int:pk>/approve/', opening_views.opening_inventory_approve, name='opening_inventory_approve'),
    path('opening-inventory/<int:pk>/post/', opening_views.opening_inventory_post, name='opening_inventory_post'),
    path('opening-inventory/<int:pk>/delete/', opening_views.opening_inventory_delete, name='opening_inventory_delete'),
    path('opening-inventory/<int:pk>/report/', opening_views.opening_inventory_report, name='opening_inventory_report'),

    # AJAX URLs
    path('ajax/get-item-cost/', opening_views.get_item_cost, name='get_item_cost'),
    path('ajax/items/search/', views.items_search, name='items_search'),
    path('ajax/items/<int:pk>/detail/', views.item_detail, name='item_detail'),
    
    # الحساب الختامي
    path('profit-centers/', views.profit_centers, name='profit_centers'),
    path('profit-centers/add/', views.profit_center_add, name='profit_center_add'),
    path('profit-centers/<int:pk>/edit/', views.profit_center_edit, name='profit_center_edit'),
    path('profit-centers/<int:pk>/delete/', views.profit_center_delete, name='profit_center_delete'),
    
    path('income-statement/', views.income_statement, name='income_statement'),
    path('balance-sheet/', views.balance_sheet, name='balance_sheet'),
    
    path('profit-distribution/', views.profit_distribution, name='profit_distribution'),
    path('profit-distribution/add/', views.profit_distribution_add, name='profit_distribution_add'),
    path('profit-distribution/<int:pk>/edit/', views.profit_distribution_edit, name='profit_distribution_edit'),
    path('profit-distribution/<int:pk>/delete/', views.profit_distribution_delete, name='profit_distribution_delete'),
    
    path('period-closure/', views.period_closure, name='period_closure'),
    path('period-closure/close/', views.period_closure_close, name='period_closure_close'),
    path('period-closure/open-new/', views.period_closure_open_new, name='period_closure_open_new'),
]
