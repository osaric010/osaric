from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # لوحة تحكم التقارير
    path('', views.reports_dashboard, name='dashboard'),
    
    # تقارير الأشخاص
    path('persons/', views.persons_reports, name='persons_reports'),
    path('persons/account-statement-invoices/', views.person_account_statement_invoices, name='person_account_statement_invoices'),
    path('persons/account-statement-detailed/', views.person_account_statement_detailed, name='person_account_statement_detailed'),
    path('persons/balances/', views.persons_balances, name='persons_balances'),
    path('persons/directory/', views.persons_directory, name='persons_directory'),
    
    # تقارير الخزينة
    path('treasury/', views.treasury_reports, name='treasury_reports'),
    path('treasury/cash-payments/', views.cash_payments_report, name='cash_payments_report'),
    path('treasury/payment-papers/', views.payment_papers_report, name='payment_papers_report'),
    path('treasury/outgoing-custody-receipts/', views.outgoing_custody_receipts_report, name='outgoing_custody_receipts_report'),
    path('treasury/expenses/', views.expenses_report, name='expenses_report'),
    path('treasury/monthly-expenses/', views.monthly_expenses_report, name='monthly_expenses_report'),
    path('treasury/cash-collections/', views.cash_collections_report, name='cash_collections_report'),
    path('treasury/collection-papers/', views.collection_papers_report, name='collection_papers_report'),
    path('treasury/incoming-custody-receipts/', views.incoming_custody_receipts_report, name='incoming_custody_receipts_report'),
    path('treasury/revenues/', views.revenues_report, name='revenues_report'),
    path('treasury/monthly-revenues/', views.monthly_revenues_report, name='monthly_revenues_report'),
    path('treasury/account-statement/', views.treasury_account_statement, name='treasury_account_statement'),
    
    # تقارير البنوك
    path('banks/', views.banks_reports, name='banks_reports'),
    path('banks/account-statement/', views.bank_account_statement, name='bank_account_statement'),
    
    # تقارير المبيعات
    path('sales/', views.sales_reports, name='sales_reports'),
    path('sales/detailed/', views.sales_detailed_report, name='sales_detailed_report'),
    path('sales/monthly/', views.sales_monthly_report, name='sales_monthly_report'),
    path('sales/summary/', views.sales_summary_report, name='sales_summary_report'),
    path('sales/profit/', views.sales_profit_report, name='sales_profit_report'),
    path('sales/discounts/', views.sales_discounts_report, name='sales_discounts_report'),
    path('sales/representative-commission/', views.representative_commission_report, name='representative_commission_report'),
    path('sales/employee-commission/', views.employee_commission_report, name='employee_commission_report'),
    path('sales/quotations-detailed/', views.quotations_detailed_report, name='quotations_detailed_report'),
    path('sales/quotations-summary/', views.quotations_summary_report, name='quotations_summary_report'),
    
    # تقارير المشتريات
    path('purchases/', views.purchases_reports, name='purchases_reports'),
    path('purchases/detailed/', views.purchases_detailed_report, name='purchases_detailed_report'),
    path('purchases/monthly/', views.purchases_monthly_report, name='purchases_monthly_report'),
    path('purchases/summary/', views.purchases_summary_report, name='purchases_summary_report'),
    path('purchases/discounts/', views.purchases_discounts_report, name='purchases_discounts_report'),
    path('purchases/supply-orders/', views.supply_orders_report, name='supply_orders_report'),
    
    # يوميات إجمالية
    path('general-journals/', views.general_journals_report, name='general_journals_report'),
    
    # تقارير المخازن
    path('warehouses/', views.warehouses_reports, name='warehouses_reports'),
    path('warehouses/stock-increases/', views.stock_increases_report, name='stock_increases_report'),
    path('warehouses/stock-decreases-detailed/', views.stock_decreases_detailed_report, name='stock_decreases_detailed_report'),
    path('warehouses/stock-decreases-monthly/', views.stock_decreases_monthly_report, name='stock_decreases_monthly_report'),
    path('warehouses/stock-decreases-renewal/', views.stock_decreases_renewal_report, name='stock_decreases_renewal_report'),
    path('warehouses/transfers-detailed/', views.warehouse_transfers_detailed_report, name='warehouse_transfers_detailed_report'),
    path('warehouses/transfers-summary/', views.warehouse_transfers_summary_report, name='warehouse_transfers_summary_report'),
    path('warehouses/production/', views.production_report, name='production_report'),
    path('warehouses/items-prices/', views.items_prices_report, name='items_prices_report'),
    path('warehouses/item-movement/', views.item_movement_report, name='item_movement_report'),
    path('warehouses/inventory/', views.inventory_report, name='inventory_report'),
    
    # تقارير الأصول الثابتة
    path('assets/', views.assets_reports, name='assets_reports'),
    path('assets/current-year-depreciation/', views.current_year_depreciation_report, name='current_year_depreciation_report'),
    path('assets/detailed/', views.assets_detailed_report, name='assets_detailed_report'),
    path('assets/summary/', views.assets_summary_report, name='assets_summary_report'),
    path('assets/sale-profits/', views.assets_sale_profits_report, name='assets_sale_profits_report'),
]
