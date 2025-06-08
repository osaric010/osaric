from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Branch(models.Model):
    """نموذج الفروع"""
    name = models.CharField(max_length=200, verbose_name="اسم الفرع")
    code = models.CharField(max_length=50, unique=True, verbose_name="كود الفرع")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    manager_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم المدير")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئ بواسطة")

    class Meta:
        verbose_name = "فرع"
        verbose_name_plural = "الفروع"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class BranchOpeningBalance(models.Model):
    """القيد الافتتاحي رصيد أول المدة للفروع"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="الفرع")
    account_type = models.CharField(max_length=50, choices=[
        ('CASH', 'نقدية'),
        ('BANK', 'بنك'),
        ('INVENTORY', 'مخزون'),
        ('RECEIVABLES', 'مدينون'),
        ('PAYABLES', 'دائنون'),
        ('OTHER', 'أخرى')
    ], verbose_name="نوع الحساب")
    account_name = models.CharField(max_length=200, verbose_name="اسم الحساب")
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))], verbose_name="مدين")
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))], verbose_name="دائن")
    date = models.DateField(verbose_name="التاريخ")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئ بواسطة")

    class Meta:
        verbose_name = "قيد افتتاحي للفرع"
        verbose_name_plural = "الأقياد الافتتاحية للفروع"
        ordering = ['-date']

    def __str__(self):
        return f"{self.branch.name} - {self.account_name}"


class GoodsTransfer(models.Model):
    """بضاعة مرحلة للفروع"""
    transfer_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التحويل")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="الفرع")
    transfer_date = models.DateField(verbose_name="تاريخ التحويل")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], verbose_name="إجمالي المبلغ")
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'معلق'),
        ('APPROVED', 'معتمد'),
        ('TRANSFERRED', 'محول'),
        ('RECEIVED', 'مستلم'),
        ('CANCELLED', 'ملغي')
    ], default='PENDING', verbose_name="الحالة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئ بواسطة")

    class Meta:
        verbose_name = "تحويل بضاعة للفرع"
        verbose_name_plural = "تحويلات البضائع للفروع"
        ordering = ['-transfer_date']

    def __str__(self):
        return f"{self.transfer_number} - {self.branch.name}"


class CashMovement(models.Model):
    """حركات النقدية بين المركز الرئيسي والفروع"""
    MOVEMENT_TYPES = [
        ('RECEIVED_FROM_BRANCH', 'نقدية واردة من الفرع'),
        ('SENT_TO_BRANCH', 'نقدية صادرة للفرع'),
    ]

    movement_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الحركة")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="الفرع")
    movement_type = models.CharField(max_length=30, choices=MOVEMENT_TYPES, verbose_name="نوع الحركة")
    movement_date = models.DateField(verbose_name="تاريخ الحركة")
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], verbose_name="المبلغ")
    description = models.TextField(verbose_name="البيان")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئ بواسطة")

    class Meta:
        verbose_name = "حركة نقدية"
        verbose_name_plural = "حركات النقدية"
        ordering = ['-movement_date']

    def __str__(self):
        return f"{self.movement_number} - {self.branch.name}"


class BankMovement(models.Model):
    """حركات البنوك بين المركز الرئيسي والفروع"""
    MOVEMENT_TYPES = [
        ('DEPOSIT_FROM_BRANCH_TREASURY', 'إيداع بنكي وارد من خزينة الفرع'),
        ('WITHDRAWAL_TO_BRANCH_TREASURY', 'مسحوب بنكي لخزينة الفرع'),
        ('DEPOSIT_FROM_BRANCH_BANK', 'إيداع بنكي وارد من بنك الفرع'),
        ('WITHDRAWAL_TO_BRANCH_BANK', 'مسحوب بنكي لبنك الفرع'),
    ]

    movement_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الحركة")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="الفرع")
    movement_type = models.CharField(max_length=50, choices=MOVEMENT_TYPES, verbose_name="نوع الحركة")
    movement_date = models.DateField(verbose_name="تاريخ الحركة")
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], verbose_name="المبلغ")
    bank_name = models.CharField(max_length=200, verbose_name="اسم البنك")
    account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="رقم الحساب")
    description = models.TextField(verbose_name="البيان")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئ بواسطة")

    class Meta:
        verbose_name = "حركة بنكية"
        verbose_name_plural = "حركات البنوك"
        ordering = ['-movement_date']

    def __str__(self):
        return f"{self.movement_number} - {self.branch.name}"


class CollectionRevenue(models.Model):
    """إيرادات تحصيلية تخص الفروع"""
    revenue_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الإيراد")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name="الفرع")
    revenue_date = models.DateField(verbose_name="تاريخ الإيراد")
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0'))], verbose_name="المبلغ")
    revenue_type = models.CharField(max_length=50, choices=[
        ('SALES', 'مبيعات'),
        ('SERVICES', 'خدمات'),
        ('COMMISSIONS', 'عمولات'),
        ('OTHER', 'أخرى')
    ], verbose_name="نوع الإيراد")
    customer_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="اسم العميل")
    description = models.TextField(verbose_name="البيان")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئ بواسطة")

    class Meta:
        verbose_name = "إيراد تحصيلي"
        verbose_name_plural = "الإيرادات التحصيلية"
        ordering = ['-revenue_date']

    def __str__(self):
        return f"{self.revenue_number} - {self.branch.name}"
