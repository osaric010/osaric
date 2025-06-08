from django.db import models
from django.contrib.auth.models import User
from definitions.models import BaseModel, Treasury, Currency
from sales.models import Customer
from purchases.models import Supplier
from decimal import Decimal


class TreasuryTransactionType(models.TextChoices):
    """أنواع معاملات الخزينة"""
    RECEIPT = 'RECEIPT', 'قبض'
    PAYMENT = 'PAYMENT', 'دفع'
    TRANSFER_IN = 'TRANSFER_IN', 'تحويل وارد'
    TRANSFER_OUT = 'TRANSFER_OUT', 'تحويل صادر'
    EXPENSE = 'EXPENSE', 'مصروف'
    REVENUE = 'REVENUE', 'إيراد'


class TreasuryTransaction(BaseModel):
    """معاملات الخزينة"""
    transaction_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المعاملة")
    date = models.DateField(verbose_name="التاريخ")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    transaction_type = models.CharField(max_length=20, choices=TreasuryTransactionType.choices,
                                        verbose_name="نوع المعاملة")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.CharField(max_length=200, verbose_name="الوصف")

    # الطرف الآخر في المعاملة
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True,
                                 verbose_name="العميل")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True, blank=True,
                                 verbose_name="المورد")

    # في حالة التحويل بين الخزائن
    to_treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, null=True, blank=True,
                                    related_name="transaction_transfers_in", verbose_name="إلى خزينة")

    # الرصيد بعد المعاملة
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                        verbose_name="الرصيد بعد المعاملة")

    reference_number = models.CharField(max_length=50, blank=True, verbose_name="رقم المرجع")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "معاملة خزينة"
        verbose_name_plural = "معاملات الخزينة"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.transaction_number} - {self.treasury.name}"


class Receipt(BaseModel):
    """التحصيل النقدي"""
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التحصيل")
    date = models.DateField(verbose_name="التاريخ")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="العميل")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    payment_method = models.CharField(max_length=20, choices=[
        ('CASH', 'نقدي'),
        ('CHECK', 'شيك'),
        ('BANK_TRANSFER', 'تحويل بنكي'),
        ('CREDIT_CARD', 'بطاقة ائتمان'),
    ], default='CASH', verbose_name="طريقة الدفع")

    # تفاصيل الشيك (في حالة الدفع بشيك)
    check_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الشيك")
    check_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الشيك")
    check_bank = models.CharField(max_length=100, blank=True, verbose_name="البنك المسحوب عليه")

    description = models.CharField(max_length=200, verbose_name="البيان")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تحصيل نقدي"
        verbose_name_plural = "التحصيل النقدي"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.receipt_number} - {self.customer.name}"


class Payment(BaseModel):
    """إيصالات الدفع"""
    payment_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الإيصال")
    date = models.DateField(verbose_name="التاريخ")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="المورد")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    payment_method = models.CharField(max_length=20, choices=[
        ('CASH', 'نقدي'),
        ('CHECK', 'شيك'),
        ('BANK_TRANSFER', 'تحويل بنكي'),
    ], default='CASH', verbose_name="طريقة الدفع")

    # تفاصيل الشيك (في حالة الدفع بشيك)
    check_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الشيك")
    check_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الشيك")

    description = models.CharField(max_length=200, verbose_name="البيان")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "إيصال دفع"
        verbose_name_plural = "إيصالات الدفع"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.payment_number} - {self.supplier.name}"


class ExpenseType(BaseModel):
    """أنواع المصروفات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود نوع المصروف")
    name = models.CharField(max_length=100, verbose_name="اسم نوع المصروف")
    description = models.TextField(blank=True, verbose_name="الوصف")

    class Meta:
        verbose_name = "نوع مصروف"
        verbose_name_plural = "أنواع المصروفات"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Expense(BaseModel):
    """المصروفات"""
    expense_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المصروف")
    date = models.DateField(verbose_name="التاريخ")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT, verbose_name="نوع المصروف")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.CharField(max_length=200, verbose_name="البيان")
    beneficiary = models.CharField(max_length=200, blank=True, verbose_name="المستفيد")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "مصروف"
        verbose_name_plural = "المصروفات"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.expense_number} - {self.expense_type.name}"


class RevenueType(BaseModel):
    """أنواع الإيرادات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود نوع الإيراد")
    name = models.CharField(max_length=100, verbose_name="اسم نوع الإيراد")
    description = models.TextField(blank=True, verbose_name="الوصف")

    class Meta:
        verbose_name = "نوع إيراد"
        verbose_name_plural = "أنواع الإيرادات"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Revenue(BaseModel):
    """الإيرادات"""
    revenue_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الإيراد")
    date = models.DateField(verbose_name="التاريخ")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    revenue_type = models.ForeignKey(RevenueType, on_delete=models.PROTECT, verbose_name="نوع الإيراد")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.CharField(max_length=200, verbose_name="البيان")
    source = models.CharField(max_length=200, blank=True, verbose_name="المصدر")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "إيراد"
        verbose_name_plural = "الإيرادات"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.revenue_number} - {self.revenue_type.name}"


class PaymentNote(BaseModel):
    """أوراق الدفع (سندات الدفع)"""
    note_number = models.CharField(max_length=50, unique=True, verbose_name="رقم السند")
    date = models.DateField(verbose_name="التاريخ")
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="المورد")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.CharField(max_length=200, verbose_name="البيان")
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'معلق'),
        ('PAID', 'مدفوع'),
        ('CANCELLED', 'ملغي'),
    ], default='PENDING', verbose_name="الحالة")
    payment_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الدفع")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "ورقة دفع"
        verbose_name_plural = "أوراق الدفع"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.note_number} - {self.supplier.name}"


class ReceiptNote(BaseModel):
    """أوراق القبض (سندات القبض)"""
    note_number = models.CharField(max_length=50, unique=True, verbose_name="رقم السند")
    date = models.DateField(verbose_name="التاريخ")
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="العميل")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.CharField(max_length=200, verbose_name="البيان")
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'معلق'),
        ('COLLECTED', 'محصل'),
        ('CANCELLED', 'ملغي'),
    ], default='PENDING', verbose_name="الحالة")
    collection_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التحصيل")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "ورقة قبض"
        verbose_name_plural = "أوراق القبض"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.note_number} - {self.customer.name}"


class CustodyReceiptOut(BaseModel):
    """إيصالات الأمانة الصادرة"""
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الإيصال")
    date = models.DateField(verbose_name="التاريخ")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    custodian = models.CharField(max_length=200, verbose_name="أمين العهدة")
    custodian_id = models.CharField(max_length=50, blank=True, verbose_name="رقم الهوية")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    purpose = models.CharField(max_length=200, verbose_name="الغرض من الأمانة")
    expected_return_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإرجاع المتوقع")
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'نشط'),
        ('RETURNED', 'مرجع'),
        ('CANCELLED', 'ملغي'),
    ], default='ACTIVE', verbose_name="الحالة")
    return_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإرجاع الفعلي")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "إيصال أمانة صادر"
        verbose_name_plural = "إيصالات الأمانة الصادرة"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.receipt_number} - {self.custodian}"


class CustodyReceiptIn(BaseModel):
    """إيصالات الأمانة الواردة"""
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الإيصال")
    date = models.DateField(verbose_name="التاريخ")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    depositor = models.CharField(max_length=200, verbose_name="المودع")
    depositor_id = models.CharField(max_length=50, blank=True, verbose_name="رقم الهوية")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    purpose = models.CharField(max_length=200, verbose_name="الغرض من الإيداع")
    expected_return_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإرجاع المتوقع")
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'نشط'),
        ('RETURNED', 'مرجع'),
        ('CANCELLED', 'ملغي'),
    ], default='ACTIVE', verbose_name="الحالة")
    return_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإرجاع الفعلي")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "إيصال أمانة وارد"
        verbose_name_plural = "إيصالات الأمانة الواردة"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.receipt_number} - {self.depositor}"


class TreasuryTransfer(BaseModel):
    """تحويل بين الخزائن"""
    transfer_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التحويل")
    date = models.DateField(verbose_name="التاريخ")
    from_treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT,
                                      related_name="transfers_out", verbose_name="من خزينة")
    to_treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT,
                                    related_name="transfers_in", verbose_name="إلى خزينة")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.CharField(max_length=200, verbose_name="البيان")
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'معلق'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ], default='PENDING', verbose_name="الحالة")
    completion_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإكمال")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تحويل بين خزائن"
        verbose_name_plural = "تحويلات بين الخزائن"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.transfer_number} - {self.from_treasury.name} إلى {self.to_treasury.name}"
