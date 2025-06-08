from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('', views.purchases_home, name='home'),
    
    # الموردين
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # فواتير المشتريات
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    
    # أوامر الشراء
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    
    # مرتجعات المشتريات
    path('returns/', views.return_list, name='return_list'),
    path('returns/create/', views.return_create, name='return_create'),
    
    # الخصومات المكتسبة
    path('earned-discounts/', views.earned_discount_list, name='earned_discount_list'),
    path('earned-discounts/create/', views.earned_discount_create, name='earned_discount_create'),
    path('earned-discounts/<int:pk>/', views.earned_discount_detail, name='earned_discount_detail'),
    
    # التقارير
    path('reports/purchases/', views.purchase_report, name='purchase_report'),
    path('reports/supplier-performance/', views.supplier_performance_report, name='supplier_performance_report'),
]
