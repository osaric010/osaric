from django.db import models
from django.contrib.auth.models import User
from definitions.models import BaseModel, Person, Currency


class Department(BaseModel):
    """الأقسام"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود القسم")
    name = models.CharField(max_length=100, verbose_name="اسم القسم")
    name_english = models.CharField(max_length=100, blank=True, verbose_name="الاسم بالإنجليزية")
    description = models.TextField(blank=True, verbose_name="الوصف")
    manager = models.ForeignKey(
        'Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_departments', verbose_name="مدير القسم"
    )
    parent_department = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='sub_departments', verbose_name="القسم الرئيسي"
    )

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Position(BaseModel):
    """المناصب والوظائف"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود المنصب")
    name = models.CharField(max_length=100, verbose_name="اسم المنصب")
    name_english = models.CharField(max_length=100, blank=True, verbose_name="الاسم بالإنجليزية")
    description = models.TextField(blank=True, verbose_name="الوصف")
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE,
        related_name='positions', verbose_name="القسم"
    )

    class Meta:
        verbose_name = "منصب"
        verbose_name_plural = "المناصب"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class SalarySystem(BaseModel):
    """أنظمة صرف المرتبات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود النظام")
    name = models.CharField(max_length=100, verbose_name="اسم النظام")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # نوع النظام
    SYSTEM_TYPES = [
        ('MONTHLY', 'شهري'),
        ('WEEKLY', 'أسبوعي'),
        ('DAILY', 'يومي'),
        ('HOURLY', 'بالساعة'),
        ('PIECE_RATE', 'بالقطعة'),
    ]
    system_type = models.CharField(
        max_length=20, choices=SYSTEM_TYPES, default='MONTHLY',
        verbose_name="نوع النظام"
    )

    # العملة
    currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT,
        verbose_name="العملة"
    )

    # الراتب الأساسي
    basic_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name="الراتب الأساسي"
    )

    # الإعدادات
    include_overtime = models.BooleanField(default=True, verbose_name="يشمل العمل الإضافي")
    overtime_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.5,
        verbose_name="معدل العمل الإضافي"
    )

    # التأمينات والضرائب
    social_insurance_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=14.0,
        verbose_name="نسبة التأمينات الاجتماعية (%)"
    )
    tax_exemption = models.DecimalField(
        max_digits=12, decimal_places=2, default=9000,
        verbose_name="الإعفاء الضريبي"
    )

    class Meta:
        verbose_name = "نظام صرف المرتب"
        verbose_name_plural = "أنظمة صرف المرتبات"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Employee(BaseModel):
    """الموظفين"""
    # ربط بنموذج الشخص
    person = models.OneToOneField(
        Person, on_delete=models.CASCADE,
        related_name='employee_profile', verbose_name="بيانات الشخص"
    )

    # معلومات الوظيفة
    employee_number = models.CharField(max_length=20, unique=True, verbose_name="رقم الموظف")
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT,
        related_name='employees', verbose_name="القسم"
    )
    position = models.ForeignKey(
        Position, on_delete=models.PROTECT,
        related_name='employees', verbose_name="المنصب"
    )
    salary_system = models.ForeignKey(
        SalarySystem, on_delete=models.PROTECT,
        related_name='employees', verbose_name="نظام المرتب"
    )

    # تواريخ مهمة
    hire_date = models.DateField(verbose_name="تاريخ التعيين")
    contract_start_date = models.DateField(null=True, blank=True, verbose_name="تاريخ بداية العقد")
    contract_end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ نهاية العقد")
    termination_date = models.DateField(null=True, blank=True, verbose_name="تاريخ انتهاء الخدمة")

    # حالة الموظف
    STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('INACTIVE', 'غير نشط'),
        ('TERMINATED', 'منتهي الخدمة'),
        ('SUSPENDED', 'موقوف'),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='ACTIVE',
        verbose_name="حالة الموظف"
    )

    # معلومات المرتب
    current_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name="المرتب الحالي"
    )

    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفين"
        ordering = ['employee_number']

    def __str__(self):
        return f"{self.person.name} ({self.employee_number})"

    @property
    def full_name(self):
        return self.person.name
