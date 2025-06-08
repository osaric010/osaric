from django.contrib import admin
from .models import (
    Currency, Warehouse, ItemCategory, Unit, Item, Bank, Treasury,
    WarehouseZone, WarehouseLocation, ItemLocation, AssetGroup, Person,
    ExpenseCategory, ExpenseItem, RevenueCategory, RevenueItem, FinancialAlert,
    ProductionStage, FinishedProduct, ProfitCenter, Printer, CompanySettings
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'exchange_rate', 'is_base_currency', 'is_active']
    list_filter = ['is_base_currency', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'location', 'manager', 'capacity', 'is_active']
    list_filter = ['is_active', 'manager']
    search_fields = ['code', 'name', 'location']
    ordering = ['name']


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'symbol']
    ordering = ['name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit', 'cost_price', 'selling_price', 'is_active']
    list_filter = ['is_active', 'category', 'unit']
    search_fields = ['code', 'name', 'barcode']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'branch', 'account_number', 'currency', 'balance', 'is_active']
    list_filter = ['is_active', 'currency']
    search_fields = ['code', 'name', 'account_number']
    ordering = ['name']


@admin.register(Treasury)
class TreasuryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'currency', 'balance', 'responsible_person', 'is_active']
    list_filter = ['is_active', 'currency']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(WarehouseZone)
class WarehouseZoneAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'warehouse', 'security_level', 'temperature_controlled', 'is_active']
    list_filter = ['warehouse', 'security_level', 'temperature_controlled', 'humidity_controlled', 'is_active']
    search_fields = ['code', 'name', 'warehouse__name']
    ordering = ['warehouse', 'name']


@admin.register(WarehouseLocation)
class WarehouseLocationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'warehouse', 'zone', 'aisle', 'rack', 'shelf', 'is_available']
    list_filter = ['warehouse', 'zone', 'is_available', 'is_pickable', 'is_receivable', 'is_active']
    search_fields = ['code', 'name', 'aisle', 'rack', 'shelf', 'bin']
    ordering = ['warehouse', 'aisle', 'rack', 'shelf']


@admin.register(ItemLocation)
class ItemLocationAdmin(admin.ModelAdmin):
    list_display = ['item', 'warehouse', 'location', 'location_type', 'priority', 'is_default', 'is_active']
    list_filter = ['warehouse', 'location_type', 'is_default', 'is_active']
    search_fields = ['item__name', 'item__code', 'location__name']
    ordering = ['item', 'warehouse', 'priority']


@admin.register(AssetGroup)
class AssetGroupAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'asset_category', 'depreciation_method', 'is_depreciable', 'is_active']
    list_filter = ['asset_category', 'depreciation_method', 'is_depreciable', 'requires_insurance', 'requires_maintenance', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'parent', 'description', 'asset_category')
        }),
        ('إعدادات الاستهلاك', {
            'fields': ('depreciation_method', 'default_useful_life', 'default_salvage_value_rate', 'is_depreciable')
        }),
        ('الحسابات المحاسبية', {
            'fields': ('asset_account', 'depreciation_account', 'accumulated_depreciation_account')
        }),
        ('الإعدادات الإضافية', {
            'fields': ('requires_insurance', 'requires_maintenance')
        }),
        ('حدود التكلفة', {
            'fields': ('min_cost_threshold', 'max_cost_threshold')
        }),
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'person_type', 'entity_type', 'phone', 'email', 'is_active_customer', 'is_active_supplier', 'is_active']
    list_filter = ['person_type', 'entity_type', 'is_active_customer', 'is_active_supplier', 'country', 'is_active']
    search_fields = ['code', 'name', 'name_english', 'phone', 'mobile', 'email', 'national_id']
    ordering = ['name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'name_english', 'person_type', 'entity_type')
        }),
        ('معلومات الهوية', {
            'fields': ('national_id', 'tax_number', 'commercial_register')
        }),
        ('معلومات الاتصال', {
            'fields': ('phone', 'mobile', 'email', 'website')
        }),
        ('العنوان', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('المعلومات المالية', {
            'fields': ('credit_limit', 'payment_terms', 'currency', 'account_receivable', 'account_payable')
        }),
        ('معلومات إضافية', {
            'fields': ('contact_person', 'contact_title', 'notes')
        }),
        ('الإعدادات', {
            'fields': ('is_active_customer', 'is_active_supplier', 'allow_credit', 'registration_date')
        }),
    )


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'requires_approval', 'max_amount', 'is_active']
    list_filter = ['category', 'requires_approval', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'description', 'category')
        }),
        ('الإعدادات المحاسبية', {
            'fields': ('default_account',)
        }),
        ('إعدادات الموافقة', {
            'fields': ('requires_approval', 'max_amount')
        }),
    )


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'expense_category', 'is_recurring', 'requires_approval', 'is_active']
    list_filter = ['expense_category', 'is_recurring', 'requires_approval', 'requires_document', 'is_active']
    search_fields = ['code', 'name', 'description', 'expense_category__name']
    ordering = ['expense_category', 'name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'expense_category', 'description')
        }),
        ('الإعدادات المحاسبية', {
            'fields': ('account_number',)
        }),
        ('إعدادات التكرار', {
            'fields': ('is_recurring', 'recurring_period')
        }),
        ('حدود المبلغ', {
            'fields': ('min_amount', 'max_amount')
        }),
        ('إعدادات الموافقة', {
            'fields': ('requires_document', 'requires_approval')
        }),
    )


@admin.register(RevenueCategory)
class RevenueCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'is_taxable', 'tax_rate', 'is_active']
    list_filter = ['category', 'is_taxable', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'description', 'category')
        }),
        ('الإعدادات المحاسبية', {
            'fields': ('default_account',)
        }),
        ('إعدادات الضرائب', {
            'fields': ('is_taxable', 'tax_rate')
        }),
    )


@admin.register(RevenueItem)
class RevenueItemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'revenue_category', 'is_recurring', 'is_taxable', 'commission_rate', 'is_active']
    list_filter = ['revenue_category', 'is_recurring', 'is_taxable', 'requires_contract', 'is_active']
    search_fields = ['code', 'name', 'description', 'revenue_category__name']
    ordering = ['revenue_category', 'name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'revenue_category', 'description')
        }),
        ('الإعدادات المحاسبية', {
            'fields': ('account_number',)
        }),
        ('إعدادات التكرار', {
            'fields': ('is_recurring', 'recurring_period')
        }),
        ('إعدادات الضرائب', {
            'fields': ('is_taxable', 'tax_rate')
        }),
        ('حدود المبلغ', {
            'fields': ('min_amount', 'max_amount')
        }),
        ('إعدادات أخرى', {
            'fields': ('requires_contract', 'commission_rate')
        }),
    )


@admin.register(ProductionStage)
class ProductionStageAdmin(admin.ModelAdmin):
    list_display = ['sequence_number', 'name', 'stage_type', 'estimated_duration_hours', 'responsible_user', 'is_critical', 'is_active']
    list_filter = ['stage_type', 'is_critical', 'requires_approval', 'requires_quality_check', 'is_active']
    search_fields = ['code', 'name', 'description']
    ordering = ['sequence_number', 'name']

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'description', 'sequence_number', 'stage_type')
        }),
        ('الموقع والمعدات', {
            'fields': ('location', 'required_equipment')
        }),
        ('الوقت والتكلفة', {
            'fields': ('estimated_duration_hours', 'setup_time_hours', 'labor_cost_per_hour', 'overhead_cost_per_hour')
        }),
        ('المسؤوليات', {
            'fields': ('responsible_user', 'cost_center')
        }),
        ('الإعدادات', {
            'fields': ('requires_approval', 'requires_quality_check', 'is_critical', 'can_run_parallel')
        }),
        ('معايير الجودة', {
            'fields': ('quality_standards', 'acceptance_criteria'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(FinishedProduct)
class FinishedProductAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'unit', 'standard_cost', 'selling_price', 'is_manufactured', 'is_sellable', 'is_active']
    list_filter = ['category', 'unit', 'is_manufactured', 'is_sellable', 'is_purchasable', 'quality_grade', 'is_active']
    search_fields = ['code', 'name', 'name_english', 'description', 'barcode', 'sku']
    ordering = ['name']

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'name_english', 'description', 'category', 'unit')
        }),
        ('معلومات المنتج', {
            'fields': ('brand', 'model', 'version', 'barcode', 'sku')
        }),
        ('المواصفات الفنية', {
            'fields': ('specifications', 'weight', 'dimensions', 'color', 'material'),
            'classes': ('collapse',)
        }),
        ('التكاليف', {
            'fields': ('standard_cost', 'material_cost', 'labor_cost', 'overhead_cost')
        }),
        ('الأسعار', {
            'fields': ('selling_price', 'wholesale_price', 'retail_price')
        }),
        ('المخزون', {
            'fields': ('min_stock', 'max_stock', 'reorder_point')
        }),
        ('الإنتاج', {
            'fields': ('production_lead_time', 'batch_size'),
            'classes': ('collapse',)
        }),
        ('الجودة', {
            'fields': ('quality_grade', 'shelf_life_days', 'certifications', 'compliance_standards'),
            'classes': ('collapse',)
        }),
        ('التعبئة والتغليف', {
            'fields': ('packaging_type', 'package_weight', 'package_dimensions', 'units_per_package'),
            'classes': ('collapse',)
        }),
        ('الحسابات المحاسبية', {
            'fields': ('inventory_account', 'cogs_account', 'revenue_account'),
            'classes': ('collapse',)
        }),
        ('الإعدادات', {
            'fields': ('is_manufactured', 'is_sellable', 'is_purchasable', 'track_serial_numbers', 'track_lot_numbers')
        }),
        ('المرفقات', {
            'fields': ('image', 'technical_drawing'),
            'classes': ('collapse',)
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(ProfitCenter)
class ProfitCenterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'level', 'manager', 'target_revenue', 'target_profit', 'is_active_period', 'is_active']
    list_filter = ['level', 'evaluation_period', 'allocate_overhead', 'overhead_allocation_method', 'include_in_reports', 'is_active']
    search_fields = ['code', 'name', 'name_english', 'description']
    ordering = ['level', 'code', 'name']

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'name_english', 'description')
        }),
        ('الهيكل التنظيمي', {
            'fields': ('parent', 'level')
        }),
        ('المسؤوليات', {
            'fields': ('manager',)
        }),
        ('معلومات الاتصال', {
            'fields': ('location', 'phone', 'email'),
            'classes': ('collapse',)
        }),
        ('الأهداف المالية', {
            'fields': ('target_revenue', 'target_profit', 'target_profit_margin', 'evaluation_period')
        }),
        ('الحسابات المحاسبية', {
            'fields': ('revenue_account', 'expense_account', 'asset_account'),
            'classes': ('collapse',)
        }),
        ('إعدادات التكلفة', {
            'fields': ('allocate_overhead', 'overhead_allocation_method', 'overhead_percentage'),
            'classes': ('collapse',)
        }),
        ('إعدادات التقارير', {
            'fields': ('include_in_reports', 'consolidate_children')
        }),
        ('الفترة الزمنية', {
            'fields': ('start_date', 'end_date')
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ['level']

    def is_active_period(self, obj):
        return obj.is_active_period
    is_active_period.boolean = True
    is_active_period.short_description = "نشط في الفترة الحالية"


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'printer_type', 'connection_type', 'location', 'is_default', 'warranty_status_display', 'is_active']
    list_filter = ['printer_type', 'connection_type', 'usage_type', 'is_default', 'is_shared', 'color_support', 'is_active']
    search_fields = ['code', 'name', 'brand', 'model', 'serial_number', 'location']
    ordering = ['name']

    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'description')
        }),
        ('معلومات الطابعة', {
            'fields': ('brand', 'model', 'serial_number', 'printer_type')
        }),
        ('الاتصال', {
            'fields': ('connection_type', 'ip_address', 'port')
        }),
        ('إعدادات الطباعة', {
            'fields': ('paper_size', 'paper_width', 'paper_height', 'dpi', 'print_speed', 'color_support', 'duplex_support')
        }),
        ('الموقع والاستخدام', {
            'fields': ('location', 'department', 'responsible_user', 'usage_type')
        }),
        ('إعدادات النظام', {
            'fields': ('is_default', 'is_shared', 'auto_cut', 'cash_drawer')
        }),
        ('معلومات الصيانة', {
            'fields': ('purchase_date', 'warranty_expiry', 'last_maintenance', 'next_maintenance'),
            'classes': ('collapse',)
        }),
        ('إحصائيات', {
            'fields': ('total_pages_printed', 'pages_this_month'),
            'classes': ('collapse',)
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('is_active', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )

    def warranty_status_display(self, obj):
        status = obj.warranty_status
        if status == 'ساري':
            return f'✅ {status}'
        elif status == 'منتهي':
            return f'❌ {status}'
        elif 'ينتهي خلال' in status:
            return f'⚠️ {status}'
        return status
    warranty_status_display.short_description = "حالة الضمان"


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'app_name', 'app_version', 'phone', 'email', 'is_active']
    search_fields = ['company_name', 'company_name_english', 'email', 'phone']

    fieldsets = (
        ('معلومات الشركة', {
            'fields': ('company_name', 'company_name_english', 'logo')
        }),
        ('معلومات الاتصال', {
            'fields': ('phone', 'mobile', 'email', 'website')
        }),
        ('العنوان', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('المعلومات القانونية', {
            'fields': ('tax_number', 'commercial_register')
        }),
        ('إعدادات التطبيق', {
            'fields': ('app_name', 'app_version', 'default_currency')
        }),
        ('إعدادات العرض', {
            'fields': ('items_per_page', 'date_format')
        }),
        ('إعدادات الأمان', {
            'fields': ('session_timeout_minutes', 'password_min_length')
        }),
        ('النسخ الاحتياطي', {
            'fields': ('auto_backup_enabled', 'backup_frequency_days'),
            'classes': ('collapse',)
        }),
        ('الإشعارات', {
            'fields': ('email_notifications_enabled', 'sms_notifications_enabled'),
            'classes': ('collapse',)
        }),
        ('إعدادات التقارير', {
            'fields': ('default_report_format', 'print_logo_on_reports', 'print_company_info'),
            'classes': ('collapse',)
        }),
        ('ملاحظات', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # السماح بإضافة إعدادات واحدة فقط
        return not CompanySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # منع حذف الإعدادات
        return False









