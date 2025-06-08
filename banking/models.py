from django.db import models
from django.contrib.auth.models import User
from definitions.models import BaseModel, Bank, Currency
from decimal import Decimal


class BankTransactionType(models.TextChoices):
    """أنواع المعاملات البنكية"""
    DEPOSIT = 'DEPOSIT', 'إيداع'
    WITHDRAWAL = 'WITHDRAWAL', 'سحب'
    TRANSFER_IN = 'TRANSFER_IN', 'تحويل وارد'
    TRANSFER_OUT = 'TRANSFER_OUT', 'تحويل صادر'
    FEE = 'FEE', 'رسوم'
    INTEREST = 'INTEREST', 'فوائد'


class BankTransaction(BaseModel):
    """المعاملات البنكية"""
    transaction_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المعاملة")
    date = models.DateField(verbose_name="التاريخ")
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name="البنك")
    transaction_type = models.CharField(max_length=20, choices=BankTransactionType.choices,
                                        verbose_name="نوع المعاملة")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.CharField(max_length=200, verbose_name="الوصف")
    reference_number = models.CharField(max_length=50, blank=True, verbose_name="رقم المرجع")

    # في حالة التحويل بين البنوك
    to_bank = models.ForeignKey(Bank, on_delete=models.PROTECT, null=True, blank=True,
                                related_name="transfers_in", verbose_name="إلى بنك")

    # الرصيد بعد المعاملة
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                        verbose_name="الرصيد بعد المعاملة")

    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'في الانتظار'),
        ('COMPLETED', 'مكتملة'),
        ('CANCELLED', 'ملغية'),
    ], default='PENDING', verbose_name="الحالة")

    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "معاملة بنكية"
        verbose_name_plural = "المعاملات البنكية"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.transaction_number} - {self.bank.name}"


class BankReconciliation(BaseModel):
    """تسوية البنوك"""
    reconciliation_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التسوية")
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name="البنك")
    statement_date = models.DateField(verbose_name="تاريخ كشف الحساب")
    statement_balance = models.DecimalField(max_digits=15, decimal_places=2,
                                            verbose_name="رصيد كشف الحساب")
    book_balance = models.DecimalField(max_digits=15, decimal_places=2,
                                       verbose_name="الرصيد الدفتري")
    difference = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="الفرق")
    status = models.CharField(max_length=20, choices=[
        ('IN_PROGRESS', 'قيد التنفيذ'),
        ('COMPLETED', 'مكتملة'),
    ], default='IN_PROGRESS', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تسوية بنك"
        verbose_name_plural = "تسويات البنوك"
        ordering = ['-statement_date', '-id']

    def save(self, *args, **kwargs):
        self.difference = self.statement_balance - self.book_balance
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reconciliation_number} - {self.bank.name}"


class BankReconciliationItem(BaseModel):
    """عناصر تسوية البنوك"""
    reconciliation = models.ForeignKey(BankReconciliation, on_delete=models.CASCADE,
                                       related_name="items", verbose_name="التسوية")
    transaction = models.ForeignKey(BankTransaction, on_delete=models.PROTECT,
                                    verbose_name="المعاملة")
    is_reconciled = models.BooleanField(default=False, verbose_name="مسوى")
    reconciliation_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التسوية")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "عنصر تسوية بنك"
        verbose_name_plural = "عناصر تسوية البنوك"

    def __str__(self):
        return f"{self.transaction.transaction_number}"


class CheckBook(BaseModel):
    """دفاتر الشيكات"""
    checkbook_number = models.CharField(max_length=50, unique=True, verbose_name="رقم دفتر الشيكات")
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name="البنك")
    start_number = models.CharField(max_length=20, verbose_name="رقم الشيك الأول")
    end_number = models.CharField(max_length=20, verbose_name="رقم الشيك الأخير")
    total_checks = models.IntegerField(verbose_name="عدد الشيكات")
    used_checks = models.IntegerField(default=0, verbose_name="الشيكات المستخدمة")
    remaining_checks = models.IntegerField(default=0, verbose_name="الشيكات المتبقية")
    issue_date = models.DateField(verbose_name="تاريخ الإصدار")
    status = models.CharField(max_length=20, choices=[
        ('ACTIVE', 'نشط'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ], default='ACTIVE', verbose_name="الحالة")

    class Meta:
        verbose_name = "دفتر شيكات"
        verbose_name_plural = "دفاتر الشيكات"
        ordering = ['-issue_date']

    def save(self, *args, **kwargs):
        self.remaining_checks = self.total_checks - self.used_checks
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.checkbook_number} - {self.bank.name}"


class Check(BaseModel):
    """الشيكات"""
    check_number = models.CharField(max_length=20, verbose_name="رقم الشيك")
    checkbook = models.ForeignKey(CheckBook, on_delete=models.PROTECT, verbose_name="دفتر الشيكات")
    date = models.DateField(verbose_name="تاريخ الشيك")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    payee = models.CharField(max_length=200, verbose_name="المستفيد")
    memo = models.CharField(max_length=200, blank=True, verbose_name="البيان")

    status = models.CharField(max_length=20, choices=[
        ('ISSUED', 'صادر'),
        ('PRESENTED', 'مقدم للبنك'),
        ('CLEARED', 'مقبوض'),
        ('BOUNCED', 'مرتد'),
        ('CANCELLED', 'ملغي'),
    ], default='ISSUED', verbose_name="الحالة")

    clearing_date = models.DateField(null=True, blank=True, verbose_name="تاريخ القبض")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "شيك"
        verbose_name_plural = "الشيكات"
        ordering = ['-date', '-check_number']
        unique_together = ['checkbook', 'check_number']

    def __str__(self):
        return f"{self.check_number} - {self.payee}"
