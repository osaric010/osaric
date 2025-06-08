from django.contrib import admin
from .models import OpeningInventory, OpeningInventoryItem


class OpeningInventoryItemInline(admin.TabularInline):
    """Inline لأصناف جرد أول المدة"""
    model = OpeningInventoryItem
    extra = 1
    fields = ['item', 'opening_quantity', 'unit_cost', 'total_value', 'batch_number', 'condition']
    readonly_fields = ['total_value']


@admin.register(OpeningInventory)
class OpeningInventoryAdmin(admin.ModelAdmin):
    """إدارة جرد أول المدة"""
    list_display = ['inventory_number', 'warehouse', 'fiscal_year', 'date', 'status', 'total_items', 'total_value']
    list_filter = ['status', 'warehouse', 'fiscal_year', 'date']
    search_fields = ['inventory_number', 'warehouse__name', 'fiscal_year', 'period_name']
    readonly_fields = ['total_items', 'total_quantity', 'total_value', 'approved_date', 'posted_date']
    inlines = [OpeningInventoryItemInline]

    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('inventory_number', 'date', 'warehouse', 'fiscal_year', 'period_name')
        }),
        ('العملة', {
            'fields': ('currency', 'exchange_rate')
        }),
        ('الحالة', {
            'fields': ('status', 'notes')
        }),
        ('الإحصائيات', {
            'fields': ('total_items', 'total_quantity', 'total_value'),
            'classes': ('collapse',)
        }),
        ('معلومات الاعتماد والترحيل', {
            'fields': ('approved_by', 'approved_date', 'posted_by', 'posted_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OpeningInventoryItem)
class OpeningInventoryItemAdmin(admin.ModelAdmin):
    """إدارة أصناف جرد أول المدة"""
    list_display = ['opening_inventory', 'item', 'opening_quantity', 'unit_cost', 'total_value', 'condition']
    list_filter = ['opening_inventory__warehouse', 'condition', 'quality_grade']
    search_fields = ['item__name', 'item__code', 'batch_number', 'serial_number']
    readonly_fields = ['total_value', 'recorded_date']
