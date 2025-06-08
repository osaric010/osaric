from django.urls import path
from . import views

app_name = 'branches'

urlpatterns = [
    # لوحة تحكم الفروع
    path('', views.branches_home, name='home'),
    
    # تعريف الفروع
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/add/', views.branch_add, name='branch_add'),
    path('branches/<int:pk>/edit/', views.branch_edit, name='branch_edit'),
    path('branches/<int:pk>/delete/', views.branch_delete, name='branch_delete'),
    
    # القيد الافتتاحي رصيد أول المدة للفروع
    path('opening-balance/', views.opening_balance, name='opening_balance'),
    path('opening-balance/add/', views.opening_balance_add, name='opening_balance_add'),
    path('opening-balance/<int:pk>/edit/', views.opening_balance_edit, name='opening_balance_edit'),
    
    # بضاعة مرحلة للفروع
    path('goods-transfer/', views.goods_transfer, name='goods_transfer'),
    path('goods-transfer/add/', views.goods_transfer_add, name='goods_transfer_add'),
    path('goods-transfer/<int:pk>/edit/', views.goods_transfer_edit, name='goods_transfer_edit'),
    path('goods-transfer/<int:pk>/delete/', views.goods_transfer_delete, name='goods_transfer_delete'),
    
    # النقدية - الخزائن
    path('cash-received/', views.cash_received, name='cash_received'),
    path('cash-received/add/', views.cash_received_add, name='cash_received_add'),
    path('cash-sent/', views.cash_sent, name='cash_sent'),
    path('cash-sent/add/', views.cash_sent_add, name='cash_sent_add'),
    
    # البنوك - خزائن الفروع
    path('bank-deposits-from-branches/', views.bank_deposits_from_branches, name='bank_deposits_from_branches'),
    path('bank-deposits-from-branches/add/', views.bank_deposits_from_branches_add, name='bank_deposits_from_branches_add'),
    path('bank-withdrawals-to-branches/', views.bank_withdrawals_to_branches, name='bank_withdrawals_to_branches'),
    path('bank-withdrawals-to-branches/add/', views.bank_withdrawals_to_branches_add, name='bank_withdrawals_to_branches_add'),
    
    # البنوك - بنوك الفروع
    path('bank-deposits-from-branch-banks/', views.bank_deposits_from_branch_banks, name='bank_deposits_from_branch_banks'),
    path('bank-deposits-from-branch-banks/add/', views.bank_deposits_from_branch_banks_add, name='bank_deposits_from_branch_banks_add'),
    path('bank-withdrawals-to-branch-banks/', views.bank_withdrawals_to_branch_banks, name='bank_withdrawals_to_branch_banks'),
    path('bank-withdrawals-to-branch-banks/add/', views.bank_withdrawals_to_branch_banks_add, name='bank_withdrawals_to_branch_banks_add'),
    
    # الإيرادات التحصيلية
    path('collection-revenues/', views.collection_revenues, name='collection_revenues'),
    path('collection-revenues/add/', views.collection_revenues_add, name='collection_revenues_add'),
    path('collection-revenues/<int:pk>/edit/', views.collection_revenues_edit, name='collection_revenues_edit'),

    # صفحة توضيحية للنقدية - الخزائن
    path('cash-treasury-demo/', views.cash_treasury_demo, name='cash_treasury_demo'),

    # المصروفات المحملة على الفروع
    path('branch-expenses/', views.branch_expenses, name='branch_expenses'),
    path('branch-expenses/add/', views.branch_expenses_add, name='branch_expenses_add'),
    path('branch-expenses/<int:pk>/edit/', views.branch_expenses_edit, name='branch_expenses_edit'),
    path('branch-expenses/<int:pk>/delete/', views.branch_expenses_delete, name='branch_expenses_delete'),

    # التقارير المتخصصة
    path('reports/branch-account-statement/', views.branch_account_statement, name='branch_account_statement'),
    path('reports/branches-balances/', views.branches_balances_report, name='branches_balances_report'),
    path('reports/branch-notifications/', views.branch_notifications_report, name='branch_notifications_report'),
]
