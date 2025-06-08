from django.contrib import admin
from .models import (
    Supplier, PurchaseInvoice, PurchaseInvoiceItem,
    PurchaseReturn, PurchaseReturnItem, PurchaseOrder, PurchaseOrderItem,
    EarnedDiscount, EarnedDiscountItem
)


class PurchaseInvoiceItemInline(admin.TabularInline):
    model = PurchaseInvoiceItem
    extra = 1
    fields = ['item', 'quantity', 'unit_cost', 'discount_percentage', 'tax_percentage', 'total_amount']
    readonly_fields = ['total_amount']


class PurchaseReturnItemInline(admin.TabularInline):
    model = PurchaseReturnItem
    extra = 1
    fields = ['item', 'quantity', 'unit_cost', 'total_amount']
    readonly_fields = ['total_amount']


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['item', 'quantity', 'unit_cost', 'total_amount', 'received_quantity']
    readonly_fields = ['total_amount']


class EarnedDiscountItemInline(admin.TabularInline):
    model = EarnedDiscountItem
    extra = 1
    fields = ['item', 'quantity', 'unit_cost', 'discount_percentage', 'discount_amount', 'total_amount']
    readonly_fields = ['discount_amount', 'total_amount']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'contact_person', 'phone', 'email', 'credit_limit', 'payment_terms']
    list_filter = ['payment_terms', 'created_at']
    search_fields = ['code', 'name', 'contact_person', 'phone', 'email']
    ordering = ['name']


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'date', 'supplier', 'total_amount', 'status', 'due_date']
    list_filter = ['status', 'date', 'supplier']
    search_fields = ['invoice_number', 'supplier_invoice_number', 'supplier__name']
    inlines = [PurchaseInvoiceItemInline]
    ordering = ['-date', '-id']


@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'date', 'supplier', 'total_amount', 'status']
    list_filter = ['status', 'date', 'supplier']
    search_fields = ['return_number', 'supplier__name']
    inlines = [PurchaseReturnItemInline]
    ordering = ['-date', '-id']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'date', 'supplier', 'total_amount', 'status', 'expected_delivery_date']
    list_filter = ['status', 'date', 'supplier']
    search_fields = ['order_number', 'supplier__name']
    inlines = [PurchaseOrderItemInline]
    ordering = ['-date', '-id']


@admin.register(EarnedDiscount)
class EarnedDiscountAdmin(admin.ModelAdmin):
    list_display = ['discount_number', 'date', 'supplier', 'discount_type', 'discount_amount', 'status']
    list_filter = ['discount_type', 'status', 'date', 'supplier']
    search_fields = ['discount_number', 'supplier__name']
    inlines = [EarnedDiscountItemInline]
    ordering = ['-date', '-id']
