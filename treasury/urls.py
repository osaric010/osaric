from django.urls import path
from . import views

app_name = 'treasury'

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.treasury_home, name='home'),
    
    # إيصالات القبض (تحصيل نقدي)
    path('receipts/', views.receipt_list, name='receipt_list'),
    path('receipts/create/', views.receipt_create, name='receipt_create'),
    path('receipts/<int:pk>/edit/', views.receipt_edit, name='receipt_edit'),
    path('receipts/<int:pk>/delete/', views.receipt_delete, name='receipt_delete'),
    
    # إيصالات الدفع (دفع نقدي)
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/create/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    
    # المصروفات
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # الإيرادات
    path('revenues/', views.revenue_list, name='revenue_list'),
    path('revenues/create/', views.revenue_create, name='revenue_create'),
    path('revenues/<int:pk>/edit/', views.revenue_edit, name='revenue_edit'),
    path('revenues/<int:pk>/delete/', views.revenue_delete, name='revenue_delete'),
    
    # أوراق الدفع
    path('payment-notes/', views.payment_note_list, name='payment_note_list'),
    path('payment-notes/create/', views.payment_note_create, name='payment_note_create'),
    path('payment-notes/<int:pk>/edit/', views.payment_note_edit, name='payment_note_edit'),
    path('payment-notes/<int:pk>/delete/', views.payment_note_delete, name='payment_note_delete'),
    path('payment-notes/<int:pk>/pay/', views.payment_note_pay, name='payment_note_pay'),
    
    # أوراق القبض
    path('receipt-notes/', views.receipt_note_list, name='receipt_note_list'),
    path('receipt-notes/create/', views.receipt_note_create, name='receipt_note_create'),
    path('receipt-notes/<int:pk>/edit/', views.receipt_note_edit, name='receipt_note_edit'),
    path('receipt-notes/<int:pk>/delete/', views.receipt_note_delete, name='receipt_note_delete'),
    path('receipt-notes/<int:pk>/collect/', views.receipt_note_collect, name='receipt_note_collect'),
    
    # إيصالات الأمانة الصادرة
    path('custody-out/', views.custody_out_list, name='custody_out_list'),
    path('custody-out/create/', views.custody_out_create, name='custody_out_create'),
    path('custody-out/<int:pk>/edit/', views.custody_out_edit, name='custody_out_edit'),
    path('custody-out/<int:pk>/delete/', views.custody_out_delete, name='custody_out_delete'),
    path('custody-out/<int:pk>/return/', views.custody_out_return, name='custody_out_return'),
    
    # إيصالات الأمانة الواردة
    path('custody-in/', views.custody_in_list, name='custody_in_list'),
    path('custody-in/create/', views.custody_in_create, name='custody_in_create'),
    path('custody-in/<int:pk>/edit/', views.custody_in_edit, name='custody_in_edit'),
    path('custody-in/<int:pk>/delete/', views.custody_in_delete, name='custody_in_delete'),
    path('custody-in/<int:pk>/return/', views.custody_in_return, name='custody_in_return'),
    
    # تحويل بين الخزائن
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/create/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:pk>/edit/', views.transfer_edit, name='transfer_edit'),
    path('transfers/<int:pk>/delete/', views.transfer_delete, name='transfer_delete'),
    path('transfers/<int:pk>/complete/', views.transfer_complete, name='transfer_complete'),
    
    # أنواع المصروفات
    path('expense-types/', views.expense_type_list, name='expense_type_list'),
    path('expense-types/create/', views.expense_type_create, name='expense_type_create'),
    path('expense-types/<int:pk>/edit/', views.expense_type_edit, name='expense_type_edit'),
    path('expense-types/<int:pk>/delete/', views.expense_type_delete, name='expense_type_delete'),
    
    # أنواع الإيرادات
    path('revenue-types/', views.revenue_type_list, name='revenue_type_list'),
    path('revenue-types/create/', views.revenue_type_create, name='revenue_type_create'),
    path('revenue-types/<int:pk>/edit/', views.revenue_type_edit, name='revenue_type_edit'),
    path('revenue-types/<int:pk>/delete/', views.revenue_type_delete, name='revenue_type_delete'),
    
    # تقارير
    path('reports/', views.treasury_reports, name='reports'),
    path('reports/transactions/', views.transaction_report, name='transaction_report'),
    path('reports/balance/', views.balance_report, name='balance_report'),
]
