from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from definitions.models import BaseModel, Item, Warehouse, Currency
from decimal import Decimal


class StockMovementType(models.TextChoices):
    """أنواع حركات المخزون"""
    IN = 'IN', 'إدخال'
    OUT = 'OUT', 'إخراج'
    TRANSFER = 'TRANSFER', 'تحويل'
    ADJUSTMENT = 'ADJUSTMENT', 'تسوية'
    PRODUCTION = 'PRODUCTION', 'إنتاج'
    OPENING = 'OPENING', 'جرد افتتاحي'


class StockMovement(BaseModel):
    """حركات المخزون"""
    movement_type = models.CharField(max_length=20, choices=StockMovementType.choices,
                                     verbose_name="نوع الحركة")
    reference_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المرجع")
    date = models.DateField(verbose_name="التاريخ")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")

    class Meta:
        verbose_name = "حركة مخزون"
        verbose_name_plural = "حركات المخزون"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.reference_number} - {self.get_movement_type_display()}"


class StockMovementItem(BaseModel):
    """أصناف حركات المخزون"""
    movement = models.ForeignKey(StockMovement, on_delete=models.CASCADE,
                                 related_name="items", verbose_name="الحركة")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي التكلفة")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")

    class Meta:
        verbose_name = "صنف حركة مخزون"
        verbose_name_plural = "أصناف حركات المخزون"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class Stock(BaseModel):
    """أرصدة المخزون"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="المخزن")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                   verbose_name="الكمية")
    reserved_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                            verbose_name="الكمية المحجوزة")
    available_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                             verbose_name="الكمية المتاحة")
    average_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="متوسط التكلفة")
    last_movement_date = models.DateTimeField(null=True, blank=True,
                                              verbose_name="تاريخ آخر حركة")

    class Meta:
        verbose_name = "رصيد مخزون"
        verbose_name_plural = "أرصدة المخزون"
        unique_together = ['warehouse', 'item']

    def save(self, *args, **kwargs):
        self.available_quantity = self.quantity - self.reserved_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.warehouse.name} - {self.item.name}: {self.quantity}"


class StockTransfer(BaseModel):
    """تحويلات المخزون"""
    transfer_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التحويل")
    date = models.DateField(verbose_name="التاريخ")
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT,
                                       related_name="transfers_out",
                                       verbose_name="من مخزن")
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT,
                                     related_name="transfers_in",
                                     verbose_name="إلى مخزن")
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'في الانتظار'),
        ('APPROVED', 'معتمد'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ], default='PENDING', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تحويل مخزون"
        verbose_name_plural = "تحويلات المخزون"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.transfer_number} - {self.from_warehouse} إلى {self.to_warehouse}"


class StockTransferItem(BaseModel):
    """أصناف تحويلات المخزون"""
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE,
                                 related_name="items", verbose_name="التحويل")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")

    class Meta:
        verbose_name = "صنف تحويل مخزون"
        verbose_name_plural = "أصناف تحويلات المخزون"

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class StockAdjustment(BaseModel):
    """تسويات المخزون"""
    adjustment_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التسوية")
    date = models.DateField(verbose_name="التاريخ")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    reason = models.CharField(max_length=200, verbose_name="السبب")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تسوية مخزون"
        verbose_name_plural = "تسويات المخزون"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.adjustment_number} - {self.warehouse}"


class StockAdjustmentItem(BaseModel):
    """أصناف تسويات المخزون"""
    adjustment = models.ForeignKey(StockAdjustment, on_delete=models.CASCADE,
                                   related_name="items", verbose_name="التسوية")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    book_quantity = models.DecimalField(max_digits=15, decimal_places=3,
                                        verbose_name="الكمية الدفترية")
    actual_quantity = models.DecimalField(max_digits=15, decimal_places=3,
                                          verbose_name="الكمية الفعلية")
    difference = models.DecimalField(max_digits=15, decimal_places=3,
                                     verbose_name="الفرق")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")

    class Meta:
        verbose_name = "صنف تسوية مخزون"
        verbose_name_plural = "أصناف تسويات المخزون"

    def save(self, *args, **kwargs):
        self.difference = self.actual_quantity - self.book_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - فرق: {self.difference}"


class StockIncrease(BaseModel):
    """إذن إضافة الزيادات"""
    increase_number = models.CharField(max_length=50, unique=True, verbose_name="رقم إذن الزيادة")
    date = models.DateField(verbose_name="التاريخ")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    reason = models.CharField(max_length=200, verbose_name="سبب الزيادة")
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('APPROVED', 'معتمد'),
        ('APPLIED', 'مطبق'),
        ('CANCELLED', 'ملغي'),
    ], default='DRAFT', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="approved_increases", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")

    class Meta:
        verbose_name = "إذن إضافة زيادة"
        verbose_name_plural = "أذون إضافة الزيادات"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.increase_number} - {self.warehouse}"


class StockIncreaseItem(BaseModel):
    """أصناف إذن إضافة الزيادات"""
    increase = models.ForeignKey(StockIncrease, on_delete=models.CASCADE,
                                 related_name="items", verbose_name="إذن الزيادة")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية المضافة")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي التكلفة")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "صنف إذن زيادة"
        verbose_name_plural = "أصناف أذون الزيادات"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class StockDecrease(BaseModel):
    """إذن صرف النواقص"""
    decrease_number = models.CharField(max_length=50, unique=True, verbose_name="رقم إذن النقص")
    date = models.DateField(verbose_name="التاريخ")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    reason = models.CharField(max_length=200, verbose_name="سبب النقص")
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('APPROVED', 'معتمد'),
        ('APPLIED', 'مطبق'),
        ('CANCELLED', 'ملغي'),
    ], default='DRAFT', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="approved_decreases", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")

    class Meta:
        verbose_name = "إذن صرف نقص"
        verbose_name_plural = "أذون صرف النواقص"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.decrease_number} - {self.warehouse}"


class StockDecreaseItem(BaseModel):
    """أصناف إذن صرف النواقص"""
    decrease = models.ForeignKey(StockDecrease, on_delete=models.CASCADE,
                                 related_name="items", verbose_name="إذن النقص")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية المنقصة")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي التكلفة")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "صنف إذن نقص"
        verbose_name_plural = "أصناف أذون النواقص"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class GoodsReceivedOnLoan(BaseModel):
    """بضاعة مضافة سلفة من الغير"""
    loan_number = models.CharField(max_length=50, unique=True, verbose_name="رقم السلفة")
    date = models.DateField(verbose_name="التاريخ")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    lender_name = models.CharField(max_length=200, verbose_name="اسم المُقرض")
    lender_phone = models.CharField(max_length=20, blank=True, verbose_name="هاتف المُقرض")
    lender_address = models.TextField(blank=True, verbose_name="عنوان المُقرض")
    loan_reason = models.CharField(max_length=200, verbose_name="سبب السلفة")
    expected_return_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإرجاع المتوقع")
    status = models.CharField(max_length=20, choices=[
        ('RECEIVED', 'مستلمة'),
        ('PARTIAL_RETURNED', 'مرتجعة جزئياً'),
        ('RETURNED', 'مرتجعة بالكامل'),
        ('OVERDUE', 'متأخرة'),
        ('CANCELLED', 'ملغاة'),
    ], default='RECEIVED', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_estimated_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                verbose_name="إجمالي القيمة التقديرية")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="approved_loans_received", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")

    class Meta:
        verbose_name = "بضاعة مضافة سلفة من الغير"
        verbose_name_plural = "بضائع مضافة سلفة من الغير"
        ordering = ['-date', '-id']

    @property
    def is_overdue(self):
        """التحقق من تأخر الإرجاع"""
        if self.expected_return_date and self.status in ['RECEIVED', 'PARTIAL_RETURNED']:
            from datetime import date
            return date.today() > self.expected_return_date
        return False

    @property
    def days_until_return(self):
        """عدد الأيام المتبقية للإرجاع"""
        if self.expected_return_date and self.status in ['RECEIVED', 'PARTIAL_RETURNED']:
            from datetime import date
            delta = self.expected_return_date - date.today()
            return delta.days
        return None

    def __str__(self):
        return f"{self.loan_number} - {self.lender_name}"


class GoodsReceivedOnLoanItem(BaseModel):
    """أصناف البضاعة المضافة سلفة من الغير"""
    loan = models.ForeignKey(GoodsReceivedOnLoan, on_delete=models.CASCADE,
                             related_name="items", verbose_name="السلفة")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity_received = models.DecimalField(max_digits=15, decimal_places=3,
                                            verbose_name="الكمية المستلمة")
    quantity_returned = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                            verbose_name="الكمية المرتجعة")
    estimated_unit_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                               verbose_name="القيمة التقديرية للوحدة")
    total_estimated_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                verbose_name="إجمالي القيمة التقديرية")
    condition_received = models.CharField(max_length=100, blank=True,
                                          verbose_name="حالة البضاعة عند الاستلام")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "صنف بضاعة سلفة"
        verbose_name_plural = "أصناف بضائع السلف"

    @property
    def quantity_remaining(self):
        """الكمية المتبقية"""
        return self.quantity_received - self.quantity_returned

    @property
    def is_fully_returned(self):
        """هل تم إرجاع الكمية بالكامل"""
        return self.quantity_returned >= self.quantity_received

    def save(self, *args, **kwargs):
        self.total_estimated_value = self.quantity_received * self.estimated_unit_value
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity_received}"


class GoodsIssuedOnLoan(BaseModel):
    """بضاعة منصرفة سلفة لدى الغير"""
    loan_number = models.CharField(max_length=50, unique=True, verbose_name="رقم السلفة")
    date = models.DateField(verbose_name="التاريخ")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    borrower_name = models.CharField(max_length=200, verbose_name="اسم المُستعير")
    borrower_phone = models.CharField(max_length=20, blank=True, verbose_name="هاتف المُستعير")
    borrower_address = models.TextField(blank=True, verbose_name="عنوان المُستعير")
    loan_reason = models.CharField(max_length=200, verbose_name="سبب السلفة")
    expected_return_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإرجاع المتوقع")
    status = models.CharField(max_length=20, choices=[
        ('ISSUED', 'منصرفة'),
        ('PARTIAL_RETURNED', 'مرتجعة جزئياً'),
        ('RETURNED', 'مرتجعة بالكامل'),
        ('OVERDUE', 'متأخرة'),
        ('CANCELLED', 'ملغاة'),
    ], default='ISSUED', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_estimated_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                verbose_name="إجمالي القيمة التقديرية")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="approved_loans_issued", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")

    class Meta:
        verbose_name = "بضاعة منصرفة سلفة لدى الغير"
        verbose_name_plural = "بضائع منصرفة سلفة لدى الغير"
        ordering = ['-date', '-id']

    @property
    def is_overdue(self):
        """التحقق من تأخر الإرجاع"""
        if self.expected_return_date and self.status in ['ISSUED', 'PARTIAL_RETURNED']:
            from datetime import date
            return date.today() > self.expected_return_date
        return False

    @property
    def days_until_return(self):
        """عدد الأيام المتبقية للإرجاع"""
        if self.expected_return_date and self.status in ['ISSUED', 'PARTIAL_RETURNED']:
            from datetime import date
            delta = self.expected_return_date - date.today()
            return delta.days
        return None

    def __str__(self):
        return f"{self.loan_number} - {self.borrower_name}"


class GoodsIssuedOnLoanItem(BaseModel):
    """أصناف البضاعة المنصرفة سلفة لدى الغير"""
    loan = models.ForeignKey(GoodsIssuedOnLoan, on_delete=models.CASCADE,
                             related_name="items", verbose_name="السلفة")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity_issued = models.DecimalField(max_digits=15, decimal_places=3,
                                          verbose_name="الكمية المنصرفة")
    quantity_returned = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                            verbose_name="الكمية المرتجعة")
    estimated_unit_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                               verbose_name="القيمة التقديرية للوحدة")
    total_estimated_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                verbose_name="إجمالي القيمة التقديرية")
    condition_issued = models.CharField(max_length=100, blank=True,
                                        verbose_name="حالة البضاعة عند الصرف")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "صنف بضاعة سلفة منصرفة"
        verbose_name_plural = "أصناف بضائع السلف المنصرفة"

    @property
    def quantity_remaining(self):
        """الكمية المتبقية"""
        return self.quantity_issued - self.quantity_returned

    @property
    def is_fully_returned(self):
        """هل تم إرجاع الكمية بالكامل"""
        return self.quantity_returned >= self.quantity_issued

    def save(self, *args, **kwargs):
        self.total_estimated_value = self.quantity_issued * self.estimated_unit_value
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity_issued}"


class WarehouseTransfer(BaseModel):
    """تحويل بين المخازن"""
    transfer_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التحويل")
    date = models.DateField(verbose_name="التاريخ")
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT,
                                       related_name="warehouse_transfers_out", verbose_name="من مخزن")
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT,
                                     related_name="warehouse_transfers_in", verbose_name="إلى مخزن")
    transfer_reason = models.CharField(max_length=200, verbose_name="سبب التحويل")
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('APPROVED', 'معتمد'),
        ('IN_TRANSIT', 'في الطريق'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ], default='DRAFT', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_estimated_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                verbose_name="إجمالي القيمة التقديرية")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="approved_transfers", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")
    shipped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="shipped_transfers", verbose_name="شحن بواسطة")
    shipped_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الشحن")
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="received_transfers", verbose_name="استلم بواسطة")
    received_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاستلام")

    class Meta:
        verbose_name = "تحويل بين المخازن"
        verbose_name_plural = "تحويلات بين المخازن"
        ordering = ['-date', '-id']

    def clean(self):
        if self.from_warehouse == self.to_warehouse:
            from django.core.exceptions import ValidationError
            raise ValidationError('لا يمكن التحويل من وإلى نفس المخزن')

    @property
    def can_be_edited(self):
        """هل يمكن تعديل التحويل"""
        return self.status in ['DRAFT']

    @property
    def can_be_approved(self):
        """هل يمكن اعتماد التحويل"""
        return self.status == 'DRAFT'

    @property
    def can_be_shipped(self):
        """هل يمكن شحن التحويل"""
        return self.status == 'APPROVED'

    @property
    def can_be_received(self):
        """هل يمكن استلام التحويل"""
        return self.status == 'IN_TRANSIT'

    @property
    def can_be_cancelled(self):
        """هل يمكن إلغاء التحويل"""
        return self.status in ['DRAFT', 'APPROVED']

    def __str__(self):
        return f"{self.transfer_number} - {self.from_warehouse} → {self.to_warehouse}"


class WarehouseTransferItem(BaseModel):
    """أصناف تحويل بين المخازن"""
    transfer = models.ForeignKey(WarehouseTransfer, on_delete=models.CASCADE,
                                 related_name="items", verbose_name="التحويل")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity_requested = models.DecimalField(max_digits=15, decimal_places=3,
                                             verbose_name="الكمية المطلوبة")
    quantity_shipped = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                           verbose_name="الكمية المشحونة")
    quantity_received = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                            verbose_name="الكمية المستلمة")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي التكلفة")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "صنف تحويل مخزن"
        verbose_name_plural = "أصناف تحويلات المخازن"

    @property
    def quantity_pending(self):
        """الكمية المعلقة (المطلوبة - المشحونة)"""
        return self.quantity_requested - self.quantity_shipped

    @property
    def quantity_in_transit(self):
        """الكمية في الطريق (المشحونة - المستلمة)"""
        return self.quantity_shipped - self.quantity_received

    @property
    def is_fully_shipped(self):
        """هل تم شحن الكمية بالكامل"""
        return self.quantity_shipped >= self.quantity_requested

    @property
    def is_fully_received(self):
        """هل تم استلام الكمية بالكامل"""
        return self.quantity_received >= self.quantity_shipped

    def save(self, *args, **kwargs):
        # حساب التكلفة الإجمالية بناءً على الكمية المطلوبة
        self.total_cost = self.quantity_requested * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity_requested}"


class ItemTransformation(BaseModel):
    """التحويل من صنف إلى صنف"""
    transformation_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التحويل")
    date = models.DateField(verbose_name="التاريخ")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    transformation_reason = models.CharField(max_length=200, verbose_name="سبب التحويل")
    transformation_type = models.CharField(max_length=20, choices=[
        ('ASSEMBLY', 'تجميع'),
        ('DISASSEMBLY', 'تفكيك'),
        ('CONVERSION', 'تحويل'),
        ('REPACKAGING', 'إعادة تعبئة'),
        ('QUALITY_CHANGE', 'تغيير جودة'),
    ], verbose_name="نوع التحويل")
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('APPROVED', 'معتمد'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ], default='DRAFT', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_input_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                            verbose_name="إجمالي قيمة المدخلات")
    total_output_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                             verbose_name="إجمالي قيمة المخرجات")
    transformation_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                              verbose_name="تكلفة التحويل")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="approved_transformations", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")

    class Meta:
        verbose_name = "تحويل من صنف إلى صنف"
        verbose_name_plural = "تحويلات من صنف إلى صنف"
        ordering = ['-date', '-id']

    @property
    def can_be_edited(self):
        """هل يمكن تعديل التحويل"""
        return self.status in ['DRAFT']

    @property
    def can_be_approved(self):
        """هل يمكن اعتماد التحويل"""
        return self.status == 'DRAFT'

    @property
    def can_be_completed(self):
        """هل يمكن إكمال التحويل"""
        return self.status == 'APPROVED'

    @property
    def can_be_cancelled(self):
        """هل يمكن إلغاء التحويل"""
        return self.status in ['DRAFT', 'APPROVED']

    @property
    def net_value_change(self):
        """صافي التغيير في القيمة"""
        return self.total_output_value - self.total_input_value - self.transformation_cost

    def __str__(self):
        return f"{self.transformation_number} - {self.get_transformation_type_display()}"


class ItemTransformationInput(BaseModel):
    """المدخلات (الأصناف المستهلكة) في التحويل"""
    transformation = models.ForeignKey(ItemTransformation, on_delete=models.CASCADE,
                                       related_name="inputs", verbose_name="التحويل")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف المستهلك")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية المستهلكة")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي التكلفة")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "مدخل تحويل صنف"
        verbose_name_plural = "مدخلات تحويل الأصناف"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} (مدخل)"


class ItemTransformationOutput(BaseModel):
    """المخرجات (الأصناف المنتجة) في التحويل"""
    transformation = models.ForeignKey(ItemTransformation, on_delete=models.CASCADE,
                                       related_name="outputs", verbose_name="التحويل")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف المنتج")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية المنتجة")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي التكلفة")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "مخرج تحويل صنف"
        verbose_name_plural = "مخرجات تحويل الأصناف"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} (مخرج)"


class ManufacturingOrder(BaseModel):
    """أمر إنتاج تام تصنيع"""
    order_number = models.CharField(max_length=50, unique=True, verbose_name="رقم أمر الإنتاج")
    date = models.DateField(verbose_name="التاريخ")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    product_item = models.ForeignKey(Item, on_delete=models.PROTECT,
                                     related_name="manufacturing_orders", verbose_name="المنتج النهائي")
    quantity_to_produce = models.DecimalField(max_digits=15, decimal_places=3,
                                              verbose_name="الكمية المطلوب إنتاجها")
    quantity_produced = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                            verbose_name="الكمية المنتجة")
    production_cost_per_unit = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                   verbose_name="تكلفة الإنتاج للوحدة")
    total_production_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                verbose_name="إجمالي تكلفة الإنتاج")

    # تكاليف إضافية
    operating_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                           verbose_name="مصاريف التشغيل")
    labor_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                   verbose_name="تكلفة العمالة")
    overhead_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                      verbose_name="التكاليف العامة")

    # مخزن الإنتاج التام
    finished_goods_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT,
                                                related_name="finished_production_orders",
                                                null=True, blank=True,
                                                verbose_name="مخزن الإنتاج التام")

    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('APPROVED', 'معتمد'),
        ('IN_PRODUCTION', 'قيد الإنتاج'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ], default='DRAFT', verbose_name="الحالة")
    priority = models.CharField(max_length=20, choices=[
        ('LOW', 'منخفضة'),
        ('NORMAL', 'عادية'),
        ('HIGH', 'عالية'),
        ('URGENT', 'عاجلة'),
    ], default='NORMAL', verbose_name="الأولوية")
    expected_completion_date = models.DateField(null=True, blank=True,
                                                verbose_name="تاريخ الإنجاز المتوقع")
    actual_completion_date = models.DateField(null=True, blank=True,
                                              verbose_name="تاريخ الإنجاز الفعلي")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_material_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                              verbose_name="إجمالي تكلفة المواد")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي التكلفة")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="approved_manufacturing_orders", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="started_manufacturing_orders", verbose_name="بدأ الإنتاج بواسطة")
    started_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ بدء الإنتاج")
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="completed_manufacturing_orders", verbose_name="أكمل الإنتاج بواسطة")
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ إكمال الإنتاج")

    class Meta:
        verbose_name = "أمر إنتاج تام تصنيع"
        verbose_name_plural = "أوامر إنتاج تام تصنيع"
        ordering = ['-date', '-id']

    @property
    def can_be_edited(self):
        """هل يمكن تعديل أمر الإنتاج"""
        return self.status in ['DRAFT']

    @property
    def can_be_approved(self):
        """هل يمكن اعتماد أمر الإنتاج"""
        return self.status == 'DRAFT'

    @property
    def can_be_started(self):
        """هل يمكن بدء الإنتاج"""
        return self.status == 'APPROVED'

    @property
    def can_be_completed(self):
        """هل يمكن إكمال الإنتاج"""
        return self.status == 'IN_PRODUCTION'

    @property
    def can_be_cancelled(self):
        """هل يمكن إلغاء أمر الإنتاج"""
        return self.status in ['DRAFT', 'APPROVED', 'IN_PRODUCTION']

    @property
    def completion_percentage(self):
        """نسبة الإنجاز"""
        if self.quantity_to_produce > 0:
            return (self.quantity_produced / self.quantity_to_produce) * 100
        return 0

    @property
    def is_overdue(self):
        """هل الأمر متأخر"""
        if self.expected_completion_date and self.status in ['APPROVED', 'IN_PRODUCTION']:
            from datetime import date
            return date.today() > self.expected_completion_date
        return False

    @property
    def total_material_cost(self):
        """إجمالي تكلفة المواد الخام"""
        return sum(material.total_cost for material in self.materials.all())

    @property
    def total_additional_costs(self):
        """إجمالي التكاليف الإضافية"""
        return self.operating_expenses + self.labor_cost + self.overhead_cost

    @property
    def total_cost(self):
        """إجمالي التكلفة الشاملة"""
        return self.total_material_cost + self.total_additional_costs

    @property
    def cost_per_unit(self):
        """تكلفة الوحدة الواحدة"""
        if self.quantity_to_produce > 0:
            return self.total_cost / self.quantity_to_produce
        return 0

    @property
    def materials_available(self):
        """هل المواد الخام متوفرة"""
        for material in self.materials.all():
            # التحقق من توفر المادة في المخزن
            try:
                stock = Stock.objects.get(warehouse=self.warehouse, item=material.material)
                if stock.available_quantity < material.quantity_required:
                    return False
            except Stock.DoesNotExist:
                return False
        return True

    @property
    def days_until_completion(self):
        """عدد الأيام المتبقية للإنجاز"""
        if self.expected_completion_date and self.status in ['APPROVED', 'IN_PRODUCTION']:
            from datetime import date
            delta = self.expected_completion_date - date.today()
            return delta.days
        return None

    def start_production(self):
        """بدء عملية الإنتاج"""
        if not self.can_be_started:
            raise ValueError("لا يمكن بدء الإنتاج في الحالة الحالية")

        if not self.materials_available:
            raise ValueError("المواد الخام غير متوفرة بالكمية المطلوبة")

        # حجز المواد الخام
        for material in self.materials.all():
            try:
                stock = Stock.objects.get(warehouse=self.warehouse, item=material.material)
                stock.reserved_quantity += material.quantity_required
                stock.available_quantity -= material.quantity_required
                stock.save()
            except Stock.DoesNotExist:
                raise ValueError(f"المادة {material.material.name} غير موجودة في المخزن")

        self.status = 'IN_PRODUCTION'
        self.save()

    def complete_production(self, quantity_produced=None):
        """إكمال عملية الإنتاج"""
        if not self.can_be_completed:
            raise ValueError("لا يمكن إكمال الإنتاج في الحالة الحالية")

        from django.db import transaction
        from datetime import date

        if quantity_produced is None:
            quantity_produced = self.quantity_to_produce

        with transaction.atomic():
            # سحب المواد الخام من المخزن
            for material in self.materials.all():
                quantity_to_consume = (material.quantity_required * quantity_produced) / self.quantity_to_produce

                stock = Stock.objects.get(warehouse=self.warehouse, item=material.material)
                stock.quantity -= quantity_to_consume
                stock.reserved_quantity -= material.quantity_required
                stock.save()

                # تحديث الكمية المستهلكة
                material.quantity_consumed = quantity_to_consume
                material.save()

            # إضافة المنتج النهائي إلى مخزن الإنتاج التام
            finished_warehouse = self.finished_goods_warehouse or self.warehouse
            finished_stock, created = Stock.objects.get_or_create(
                warehouse=finished_warehouse,
                item=self.product_item,
                defaults={
                    'quantity': 0,
                    'average_cost': 0
                }
            )

            # حساب التكلفة الجديدة
            new_cost = self.cost_per_unit
            total_quantity = finished_stock.quantity + quantity_produced

            if total_quantity > 0:
                # حساب متوسط التكلفة المرجح
                total_value = (finished_stock.quantity * finished_stock.average_cost) + (quantity_produced * new_cost)
                finished_stock.average_cost = total_value / total_quantity

            finished_stock.quantity += quantity_produced
            finished_stock.available_quantity += quantity_produced
            finished_stock.last_movement_date = date.today()
            finished_stock.save()

            # تحديث بيانات أمر الإنتاج
            self.quantity_produced = quantity_produced
            self.actual_completion_date = date.today()
            self.status = 'COMPLETED'
            self.save()

    def save(self, *args, **kwargs):
        # حساب التكلفة الإجمالية
        if self.quantity_to_produce > 0:
            self.total_production_cost = self.total_cost
            self.production_cost_per_unit = self.cost_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.product_item.name}"


class ManufacturingOrderMaterial(BaseModel):
    """المواد الخام المطلوبة لأمر الإنتاج"""
    order = models.ForeignKey(ManufacturingOrder, on_delete=models.CASCADE,
                              related_name="materials", verbose_name="أمر الإنتاج")
    material = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="المادة الخام")
    quantity_required = models.DecimalField(max_digits=15, decimal_places=3,
                                            verbose_name="الكمية المطلوبة")
    quantity_consumed = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                            verbose_name="الكمية المستهلكة")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي التكلفة")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "مادة خام لأمر الإنتاج"
        verbose_name_plural = "مواد خام لأوامر الإنتاج"

    @property
    def quantity_remaining(self):
        """الكمية المتبقية"""
        return self.quantity_required - self.quantity_consumed

    @property
    def is_fully_consumed(self):
        """هل تم استهلاك الكمية بالكامل"""
        return self.quantity_consumed >= self.quantity_required

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity_required * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material.name} - {self.quantity_required}"


class PhysicalInventory(BaseModel):
    """الجرد الفعلي للمخزون"""
    inventory_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الجرد")
    date = models.DateField(verbose_name="تاريخ الجرد")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    inventory_type = models.CharField(max_length=20, choices=[
        ('FULL', 'جرد شامل'),
        ('PARTIAL', 'جرد جزئي'),
        ('CYCLE', 'جرد دوري'),
        ('SPOT', 'جرد عشوائي'),
        ('OPENING', 'جرد افتتاحي'),
    ], default='FULL', verbose_name="نوع الجرد")
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('IN_PROGRESS', 'قيد التنفيذ'),
        ('COMPLETED', 'مكتمل'),
        ('APPROVED', 'معتمد'),
        ('CANCELLED', 'ملغي'),
    ], default='DRAFT', verbose_name="الحالة")
    reason = models.CharField(max_length=200, verbose_name="سبب الجرد")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    total_items_counted = models.IntegerField(default=0, verbose_name="عدد الأصناف المجردة")
    total_discrepancies = models.IntegerField(default=0, verbose_name="عدد الفروقات")
    total_value_difference = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                                 verbose_name="إجمالي قيمة الفروقات")
    # حقول خاصة بالجرد الافتتاحي
    financial_year = models.CharField(max_length=10, blank=True, verbose_name="السنة المالية")
    total_opening_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                              verbose_name="إجمالي قيمة الافتتاح")
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="started_inventories", verbose_name="بدأ الجرد بواسطة")
    started_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ بدء الجرد")
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="completed_inventories", verbose_name="أكمل الجرد بواسطة")
    completed_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ إكمال الجرد")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="approved_inventories", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")

    class Meta:
        verbose_name = "جرد فعلي"
        verbose_name_plural = "جرد فعلي"
        ordering = ['-date', '-id']

    @property
    def can_be_edited(self):
        """هل يمكن تعديل الجرد"""
        return self.status in ['DRAFT']

    @property
    def can_be_started(self):
        """هل يمكن بدء الجرد"""
        return self.status == 'DRAFT'

    @property
    def can_be_completed(self):
        """هل يمكن إكمال الجرد"""
        return self.status == 'IN_PROGRESS'

    @property
    def can_be_approved(self):
        """هل يمكن اعتماد الجرد"""
        return self.status == 'COMPLETED'

    @property
    def can_be_cancelled(self):
        """هل يمكن إلغاء الجرد"""
        return self.status in ['DRAFT', 'IN_PROGRESS']

    @property
    def has_discrepancies(self):
        """هل يوجد فروقات في الجرد"""
        return self.total_discrepancies > 0

    @property
    def discrepancy_percentage(self):
        """نسبة الفروقات"""
        if self.total_items_counted > 0:
            return (self.total_discrepancies / self.total_items_counted) * 100
        return 0

    @property
    def accuracy_percentage(self):
        """نسبة الدقة"""
        return 100 - self.discrepancy_percentage

    @property
    def is_opening_inventory(self):
        """هل هو جرد افتتاحي"""
        return self.inventory_type == 'OPENING'

    def apply_opening_inventory(self, user):
        """تطبيق الجرد الافتتاحي على المخزون"""
        if not self.is_opening_inventory:
            raise ValueError("هذا ليس جرد افتتاحي")

        if self.status != 'COMPLETED':
            raise ValueError("يجب إكمال الجرد أولاً")

        with transaction.atomic():
            # إنشاء حركة مخزون للجرد الافتتاحي
            movement = StockMovement.objects.create(
                movement_type='OPENING',
                reference_number=self.inventory_number,
                date=self.date,
                warehouse=self.warehouse,
                notes=f'جرد افتتاحي - {self.financial_year}',
                total_amount=self.total_opening_value,
                created_by=user
            )

            # تطبيق كل صنف
            for item in self.items.filter(counted_quantity__gt=0):
                # إنشاء حركة للصنف
                StockMovementItem.objects.create(
                    movement=movement,
                    item=item.item,
                    quantity=item.counted_quantity,
                    unit_cost=item.unit_cost,
                    total_cost=item.counted_quantity * item.unit_cost,
                    expiry_date=item.expiry_date,
                    batch_number=item.batch_number
                )

                # تحديث أو إنشاء رصيد المخزون
                stock, created = Stock.objects.get_or_create(
                    warehouse=self.warehouse,
                    item=item.item,
                    defaults={
                        'quantity': item.counted_quantity,
                        'average_cost': item.unit_cost,
                        'last_movement_date': timezone.now()
                    }
                )

                if not created:
                    # إذا كان الرصيد موجود، نضيف الكمية الجديدة
                    total_value = (stock.quantity * stock.average_cost) + (item.counted_quantity * item.unit_cost)
                    stock.quantity += item.counted_quantity
                    stock.average_cost = total_value / stock.quantity if stock.quantity > 0 else 0
                    stock.last_movement_date = timezone.now()
                    stock.save()

            # تحديث حالة الجرد
            self.status = 'APPROVED'
            self.approved_by = user
            self.approved_date = timezone.now()
            self.save()

    def calculate_opening_totals(self):
        """حساب إجماليات الجرد الافتتاحي"""
        if self.is_opening_inventory:
            items = self.items.all()
            self.total_items_counted = items.count()
            self.total_opening_value = sum(
                (item.counted_quantity or 0) * item.unit_cost
                for item in items
            )
            self.save()

    def __str__(self):
        return f"{self.inventory_number} - {self.warehouse.name}"


class PhysicalInventoryItem(BaseModel):
    """أصناف الجرد الفعلي"""
    inventory = models.ForeignKey(PhysicalInventory, on_delete=models.CASCADE,
                                  related_name="items", verbose_name="الجرد")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    system_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                          verbose_name="الكمية في النظام")
    counted_quantity = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True,
                                           verbose_name="الكمية المجردة")
    difference_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                              verbose_name="فرق الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="تكلفة الوحدة")
    difference_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                           verbose_name="قيمة الفرق")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    location = models.CharField(max_length=100, blank=True, verbose_name="الموقع في المخزن")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    counted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="جرد بواسطة")
    counted_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الجرد")
    is_counted = models.BooleanField(default=False, verbose_name="تم الجرد")
    discrepancy_reason = models.CharField(max_length=200, blank=True, verbose_name="سبب الفرق")

    class Meta:
        verbose_name = "صنف جرد فعلي"
        verbose_name_plural = "أصناف جرد فعلي"
        unique_together = ['inventory', 'item']

    @property
    def has_discrepancy(self):
        """هل يوجد فرق في الكمية"""
        return abs(self.difference_quantity) > 0.001

    @property
    def discrepancy_type(self):
        """نوع الفرق"""
        if self.difference_quantity > 0:
            return 'SURPLUS'  # زيادة
        elif self.difference_quantity < 0:
            return 'SHORTAGE'  # نقص
        else:
            return 'MATCH'  # مطابق

    @property
    def discrepancy_type_display(self):
        """عرض نوع الفرق"""
        if self.difference_quantity > 0:
            return 'زيادة'
        elif self.difference_quantity < 0:
            return 'نقص'
        else:
            return 'مطابق'

    def save(self, *args, **kwargs):
        # حساب الفرق في الكمية والقيمة
        if self.counted_quantity is not None:
            self.difference_quantity = self.counted_quantity - self.system_quantity
            self.difference_value = self.difference_quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.inventory.inventory_number}"


# تم نقل نماذج الجرد الافتتاحي إلى تطبيق الحسابات العامة (accounting)
