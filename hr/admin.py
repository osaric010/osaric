from django.contrib import admin
from .models import Department, Position, SalarySystem, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'manager', 'parent_department', 'is_active']
    list_filter = ['parent_department', 'is_active']
    search_fields = ['code', 'name', 'name_english']
    ordering = ['name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'name_english', 'description')
        }),
        ('الهيكل التنظيمي', {
            'fields': ('parent_department', 'manager')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['code', 'name', 'name_english']
    ordering = ['name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'name_english', 'description')
        }),
        ('القسم', {
            'fields': ('department',)
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
    )


@admin.register(SalarySystem)
class SalarySystemAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'system_type', 'basic_salary', 'currency', 'is_active']
    list_filter = ['system_type', 'currency', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['name']
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('code', 'name', 'description', 'system_type', 'currency')
        }),
        ('الراتب الأساسي', {
            'fields': ('basic_salary',)
        }),
        ('العمل الإضافي', {
            'fields': ('include_overtime', 'overtime_rate')
        }),
        ('التأمينات والضرائب', {
            'fields': ('social_insurance_rate', 'tax_exemption')
        }),
        ('الحالة', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_number', 'full_name', 'department', 'position', 'status', 'hire_date']
    list_filter = ['department', 'position', 'status', 'salary_system']
    search_fields = ['employee_number', 'person__name', 'person__name_english']
    ordering = ['employee_number']
    fieldsets = (
        ('معلومات الموظف', {
            'fields': ('person', 'employee_number')
        }),
        ('معلومات الوظيفة', {
            'fields': ('department', 'position', 'salary_system', 'current_salary')
        }),
        ('التواريخ', {
            'fields': ('hire_date', 'contract_start_date', 'contract_end_date', 'termination_date')
        }),
        ('الحالة', {
            'fields': ('status', 'is_active')
        }),
    )
