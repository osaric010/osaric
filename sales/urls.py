from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sales_home, name='home'),

    # العملاء
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # فواتير المبيعات
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),

    # مرتجعات المبيعات
    path('returns/', views.return_list, name='return_list'),
    path('returns/create/', views.return_create, name='return_create'),

    # عروض الأسعار
    path('quotations/', views.quotation_list, name='quotation_list'),
    path('quotations/create/', views.quotation_create, name='quotation_create'),
    path('quotations/<int:pk>/', views.quotation_detail, name='quotation_detail'),

    # قوائم الأسعار
    path('price-lists/', views.price_list_list, name='price_list_list'),
    path('price-lists/create/', views.price_list_create, name='price_list_create'),

    # عرض الأسعار
    path('price-display/', views.price_display, name='price_display'),

    # التقارير
    path('reports/quotations-period/', views.quotation_period_report, name='quotation_period_report'),

    # سياسات الخصم
    path('discount-policies/', views.discount_policy_list, name='discount_policy_list'),
]
