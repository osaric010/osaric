from django.contrib import admin
from .models import (
    Customer, SalesInvoice, SalesInvoiceItem, SalesReturn, SalesReturnItem,
    PriceList, PriceListItem, Quotation, QuotationItem, DiscountPolicy
)


class SalesInvoiceItemInline(admin.TabularInline):
    model = SalesInvoiceItem
    extra = 1


class SalesReturnItemInline(admin.TabularInline):
    model = SalesReturnItem
    extra = 1


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1


class PriceListItemInline(admin.TabularInline):
    model = PriceListItem
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'phone', 'email', 'credit_limit', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name', 'phone', 'email']
    ordering = ['name']


@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'date', 'customer', 'total_amount', 'status', 'is_active']
    list_filter = ['status', 'date', 'is_active']
    search_fields = ['invoice_number', 'customer__name']
    inlines = [SalesInvoiceItemInline]
    ordering = ['-date', '-id']


@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    list_display = ['return_number', 'date', 'customer', 'total_amount', 'status', 'is_active']
    list_filter = ['status', 'date', 'is_active']
    search_fields = ['return_number', 'customer__name']
    inlines = [SalesReturnItemInline]
    ordering = ['-date', '-id']


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'price_type', 'start_date', 'end_date', 'is_default']
    list_filter = ['price_type', 'is_default']
    search_fields = ['code', 'name']
    inlines = [PriceListItemInline]
    ordering = ['name']


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'date', 'customer', 'total_amount', 'valid_until', 'status']
    list_filter = ['status', 'date']
    search_fields = ['quotation_number', 'customer__name']
    inlines = [QuotationItemInline]
    ordering = ['-date', '-id']


@admin.register(DiscountPolicy)
class DiscountPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount_type', 'discount_percentage', 'start_date', 'end_date']
    list_filter = ['discount_type']
    search_fields = ['name']
    ordering = ['name']
