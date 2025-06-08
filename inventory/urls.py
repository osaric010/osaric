from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Stock Increase URLs
    path('stock-increases/', views.stock_increase_list, name='stock_increase_list'),
    path('stock-increases/create/', views.stock_increase_create, name='stock_increase_create'),
    path('stock-increases/<int:pk>/', views.stock_increase_detail, name='stock_increase_detail'),
    path('stock-increases/<int:pk>/edit/', views.stock_increase_edit, name='stock_increase_edit'),
    path('stock-increases/<int:pk>/approve/', views.stock_increase_approve, name='stock_increase_approve'),
    path('stock-increases/<int:pk>/apply/', views.stock_increase_apply, name='stock_increase_apply'),
    path('stock-increases/<int:pk>/delete/', views.stock_increase_delete, name='stock_increase_delete'),

    # Stock Decrease URLs
    path('stock-decreases/', views.stock_decrease_list, name='stock_decrease_list'),
    path('stock-decreases/create/', views.stock_decrease_create, name='stock_decrease_create'),
    path('stock-decreases/<int:pk>/', views.stock_decrease_detail, name='stock_decrease_detail'),
    path('stock-decreases/<int:pk>/edit/', views.stock_decrease_edit, name='stock_decrease_edit'),
    path('stock-decreases/<int:pk>/approve/', views.stock_decrease_approve, name='stock_decrease_approve'),
    path('stock-decreases/<int:pk>/apply/', views.stock_decrease_apply, name='stock_decrease_apply'),
    path('stock-decreases/<int:pk>/delete/', views.stock_decrease_delete, name='stock_decrease_delete'),

    # Goods Received On Loan URLs
    path('goods-received-on-loan/', views.goods_received_on_loan_list, name='goods_received_on_loan_list'),
    path('goods-received-on-loan/create/', views.goods_received_on_loan_create, name='goods_received_on_loan_create'),
    path('goods-received-on-loan/<int:pk>/', views.goods_received_on_loan_detail, name='goods_received_on_loan_detail'),
    path('goods-received-on-loan/<int:pk>/edit/', views.goods_received_on_loan_edit, name='goods_received_on_loan_edit'),
    path('goods-received-on-loan/<int:pk>/return/', views.goods_received_on_loan_return, name='goods_received_on_loan_return'),
    path('goods-received-on-loan/<int:pk>/partial-return/', views.goods_received_on_loan_partial_return, name='goods_received_on_loan_partial_return'),
    path('goods-received-on-loan/<int:pk>/cancel/', views.goods_received_on_loan_cancel, name='goods_received_on_loan_cancel'),
    path('goods-received-on-loan/<int:pk>/delete/', views.goods_received_on_loan_delete, name='goods_received_on_loan_delete'),

    # Goods Issued On Loan URLs
    path('goods-issued-on-loan/', views.goods_issued_on_loan_list, name='goods_issued_on_loan_list'),
    path('goods-issued-on-loan/create/', views.goods_issued_on_loan_create, name='goods_issued_on_loan_create'),
    path('goods-issued-on-loan/<int:pk>/', views.goods_issued_on_loan_detail, name='goods_issued_on_loan_detail'),
    path('goods-issued-on-loan/<int:pk>/edit/', views.goods_issued_on_loan_edit, name='goods_issued_on_loan_edit'),
    path('goods-issued-on-loan/<int:pk>/return/', views.goods_issued_on_loan_return, name='goods_issued_on_loan_return'),
    path('goods-issued-on-loan/<int:pk>/partial-return/', views.goods_issued_on_loan_partial_return, name='goods_issued_on_loan_partial_return'),
    path('goods-issued-on-loan/<int:pk>/cancel/', views.goods_issued_on_loan_cancel, name='goods_issued_on_loan_cancel'),
    path('goods-issued-on-loan/<int:pk>/delete/', views.goods_issued_on_loan_delete, name='goods_issued_on_loan_delete'),

    # Warehouse Transfer URLs
    path('warehouse-transfers/', views.warehouse_transfer_list, name='warehouse_transfer_list'),
    path('warehouse-transfers/create/', views.warehouse_transfer_create, name='warehouse_transfer_create'),
    path('warehouse-transfers/<int:pk>/', views.warehouse_transfer_detail, name='warehouse_transfer_detail'),
    path('warehouse-transfers/<int:pk>/edit/', views.warehouse_transfer_edit, name='warehouse_transfer_edit'),
    path('warehouse-transfers/<int:pk>/approve/', views.warehouse_transfer_approve, name='warehouse_transfer_approve'),
    path('warehouse-transfers/<int:pk>/ship/', views.warehouse_transfer_ship, name='warehouse_transfer_ship'),
    path('warehouse-transfers/<int:pk>/receive/', views.warehouse_transfer_receive, name='warehouse_transfer_receive'),
    path('warehouse-transfers/<int:pk>/cancel/', views.warehouse_transfer_cancel, name='warehouse_transfer_cancel'),
    path('warehouse-transfers/<int:pk>/delete/', views.warehouse_transfer_delete, name='warehouse_transfer_delete'),

    # Item Transformation URLs
    path('item-transformations/', views.item_transformation_list, name='item_transformation_list'),
    path('item-transformations/create/', views.item_transformation_create, name='item_transformation_create'),
    path('item-transformations/<int:pk>/', views.item_transformation_detail, name='item_transformation_detail'),
    path('item-transformations/<int:pk>/edit/', views.item_transformation_edit, name='item_transformation_edit'),
    path('item-transformations/<int:pk>/approve/', views.item_transformation_approve, name='item_transformation_approve'),
    path('item-transformations/<int:pk>/complete/', views.item_transformation_complete, name='item_transformation_complete'),
    path('item-transformations/<int:pk>/cancel/', views.item_transformation_cancel, name='item_transformation_cancel'),
    path('item-transformations/<int:pk>/delete/', views.item_transformation_delete, name='item_transformation_delete'),

    # Manufacturing Order URLs
    path('manufacturing-orders/', views.manufacturing_order_list, name='manufacturing_order_list'),
    path('manufacturing-orders/create/', views.manufacturing_order_create, name='manufacturing_order_create'),
    path('manufacturing-orders/<int:pk>/', views.manufacturing_order_detail, name='manufacturing_order_detail'),
    path('manufacturing-orders/<int:pk>/edit/', views.manufacturing_order_edit, name='manufacturing_order_edit'),
    path('manufacturing-orders/<int:pk>/approve/', views.manufacturing_order_approve, name='manufacturing_order_approve'),
    path('manufacturing-orders/<int:pk>/start/', views.manufacturing_order_start, name='manufacturing_order_start'),
    path('manufacturing-orders/<int:pk>/complete/', views.manufacturing_order_complete, name='manufacturing_order_complete'),
    path('manufacturing-orders/<int:pk>/cancel/', views.manufacturing_order_cancel, name='manufacturing_order_cancel'),
    path('manufacturing-orders/<int:pk>/start-production/', views.start_production, name='start_production'),
    path('manufacturing-orders/<int:pk>/complete-production/', views.complete_production, name='complete_production'),
    path('manufacturing-orders/<int:pk>/materials-check/', views.production_materials_check, name='production_materials_check'),

    # الجرد الافتتاحي
    path('opening-inventory/', views.opening_inventory_list, name='opening_inventory_list'),
    path('opening-inventory/create/', views.opening_inventory_create, name='opening_inventory_create'),
    path('opening-inventory/<int:pk>/', views.opening_inventory_detail, name='opening_inventory_detail'),
    path('opening-inventory/<int:pk>/edit/', views.opening_inventory_edit, name='opening_inventory_edit'),
    path('opening-inventory/<int:pk>/add-items/', views.opening_inventory_add_items, name='opening_inventory_add_items'),
    path('opening-inventory/<int:pk>/apply/', views.opening_inventory_apply, name='opening_inventory_apply'),
    path('manufacturing-orders/<int:pk>/delete/', views.manufacturing_order_delete, name='manufacturing_order_delete'),

    # Physical Inventory URLs
    path('physical-inventory/', views.physical_inventory_list, name='physical_inventory_list'),
    path('physical-inventory/create/', views.physical_inventory_create, name='physical_inventory_create'),
    path('physical-inventory/<int:pk>/', views.physical_inventory_detail, name='physical_inventory_detail'),
    path('physical-inventory/<int:pk>/edit/', views.physical_inventory_edit, name='physical_inventory_edit'),
    path('physical-inventory/<int:pk>/start/', views.physical_inventory_start, name='physical_inventory_start'),
    path('physical-inventory/<int:pk>/count/', views.physical_inventory_count, name='physical_inventory_count'),
    path('physical-inventory/<int:pk>/count/<int:item_pk>/', views.physical_inventory_count_item, name='physical_inventory_count_item'),
    path('physical-inventory/<int:pk>/complete/', views.physical_inventory_complete, name='physical_inventory_complete'),
    path('physical-inventory/<int:pk>/approve/', views.physical_inventory_approve, name='physical_inventory_approve'),
    path('physical-inventory/<int:pk>/cancel/', views.physical_inventory_cancel, name='physical_inventory_cancel'),
    path('physical-inventory/<int:pk>/delete/', views.physical_inventory_delete, name='physical_inventory_delete'),
    path('physical-inventory/<int:pk>/report/', views.physical_inventory_report, name='physical_inventory_report'),

    # AJAX URLs
    path('items/search/', views.items_search, name='items_search'),
    path('items/<int:pk>/detail/', views.item_detail, name='item_detail'),
    path('warehouse/<int:warehouse_id>/items/', views.get_warehouse_items, name='get_warehouse_items'),
]
