from django.db import models
from django.contrib.auth.models import User
from definitions.models import BaseModel, Item, Warehouse, Currency
from decimal import Decimal


class Supplier(BaseModel):
    """الموردين"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود المورد")
    name = models.CharField(max_length=200, verbose_name="اسم المورد")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="الشخص المسؤول")
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    address = models.TextField(blank=True, verbose_name="العنوان")
    tax_number = models.CharField(max_length=50, blank=True, verbose_name="الرقم الضريبي")
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="حد الائتمان")
    payment_terms = models.IntegerField(default=0, verbose_name="شروط الدفع (أيام)")

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردين"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class PurchaseInvoice(BaseModel):
    """فواتير المشتريات"""
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة")
    supplier_invoice_number = models.CharField(max_length=50, blank=True,
                                               verbose_name="رقم فاتورة المورد")
    date = models.DateField(verbose_name="التاريخ")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="المورد")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="العملة")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000,
                                        verbose_name="سعر الصرف")

    # المبالغ
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                   verbose_name="المجموع الفرعي")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          verbose_name="مبلغ الخصم")
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="مبلغ الضريبة")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                      verbose_name="المبلغ المدفوع")
    remaining_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                           verbose_name="المبلغ المتبقي")

    # الحالة
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('CONFIRMED', 'مؤكدة'),
        ('RECEIVED', 'مستلمة'),
        ('PAID', 'مدفوعة'),
        ('CANCELLED', 'ملغية'),
    ], default='DRAFT', verbose_name="الحالة")

    due_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الاستحقاق")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "فاتورة مشتريات"
        verbose_name_plural = "فواتير المشتريات"
        ordering = ['-date', '-id']

    def save(self, *args, **kwargs):
        # تعيين العملة الافتراضية إذا لم تكن محددة
        if not self.currency_id:
            try:
                from definitions.models import Currency
                default_currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
                if default_currency:
                    self.currency = default_currency
                    self.exchange_rate = default_currency.exchange_rate
            except:
                pass

        self.remaining_amount = self.total_amount - self.paid_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.supplier.name}"


class PurchaseInvoiceItem(BaseModel):
    """أصناف فواتير المشتريات"""
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE,
                                related_name="items", verbose_name="الفاتورة")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="تكلفة الوحدة")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              verbose_name="نسبة الخصم")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          verbose_name="مبلغ الخصم")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                         verbose_name="نسبة الضريبة")
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="مبلغ الضريبة")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")

    class Meta:
        verbose_name = "صنف فاتورة مشتريات"
        verbose_name_plural = "أصناف فواتير المشتريات"

    def save(self, *args, **kwargs):
        # حساب المبالغ
        subtotal = self.quantity * self.unit_cost
        self.discount_amount = subtotal * (self.discount_percentage / Decimal('100'))
        amount_after_discount = subtotal - self.discount_amount
        self.tax_amount = amount_after_discount * (self.tax_percentage / Decimal('100'))
        self.total_amount = amount_after_discount + self.tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class PurchaseReturn(BaseModel):
    """مرتجعات المشتريات"""
    return_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المرتجع")
    date = models.DateField(verbose_name="التاريخ")
    original_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.PROTECT,
                                         null=True, blank=True,
                                         verbose_name="الفاتورة الأصلية")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="المورد")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    reason = models.CharField(max_length=200, verbose_name="سبب الإرجاع")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'في الانتظار'),
        ('APPROVED', 'معتمد'),
        ('COMPLETED', 'مكتمل'),
        ('REJECTED', 'مرفوض'),
    ], default='PENDING', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "مرتجع مشتريات"
        verbose_name_plural = "مرتجعات المشتريات"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.return_number} - {self.supplier.name}"


class PurchaseReturnItem(BaseModel):
    """أصناف مرتجعات المشتريات"""
    return_doc = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE,
                                   related_name="items", verbose_name="المرتجع")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="تكلفة الوحدة")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")

    class Meta:
        verbose_name = "صنف مرتجع مشتريات"
        verbose_name_plural = "أصناف مرتجعات المشتريات"

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class PurchaseOrder(BaseModel):
    """أوامر الشراء"""
    order_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الأمر")
    date = models.DateField(verbose_name="التاريخ")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="المورد")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    expected_delivery_date = models.DateField(null=True, blank=True,
                                              verbose_name="تاريخ التسليم المتوقع")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('SENT', 'مرسل'),
        ('CONFIRMED', 'مؤكد'),
        ('PARTIALLY_RECEIVED', 'مستلم جزئياً'),
        ('COMPLETED', 'مكتمل'),
        ('CANCELLED', 'ملغي'),
    ], default='DRAFT', verbose_name="الحالة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "أمر شراء"
        verbose_name_plural = "أوامر الشراء"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.order_number} - {self.supplier.name}"


class PurchaseOrderItem(BaseModel):
    """أصناف أوامر الشراء"""
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE,
                              related_name="items", verbose_name="الأمر")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="تكلفة الوحدة")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")
    received_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                            verbose_name="الكمية المستلمة")

    class Meta:
        verbose_name = "صنف أمر شراء"
        verbose_name_plural = "أصناف أوامر الشراء"

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class EarnedDiscount(BaseModel):
    """الخصم المكتسب"""
    DISCOUNT_TYPE_CHOICES = [
        ('VOLUME', 'خصم الكمية'),
        ('PAYMENT_TERMS', 'خصم شروط الدفع'),
        ('SEASONAL', 'خصم موسمي'),
        ('LOYALTY', 'خصم الولاء'),
        ('PROMOTIONAL', 'خصم ترويجي'),
        ('EARLY_PAYMENT', 'خصم الدفع المبكر'),
        ('BULK_ORDER', 'خصم الطلبات الكبيرة'),
        ('OTHER', 'أخرى'),
    ]

    discount_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الخصم")
    date = models.DateField(verbose_name="التاريخ")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="المورد")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES,
                                     verbose_name="نوع الخصم")

    # مرجع الخصم (فاتورة أو أمر شراء)
    reference_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.PROTECT,
                                          null=True, blank=True,
                                          verbose_name="الفاتورة المرجعية")
    reference_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT,
                                        null=True, blank=True,
                                        verbose_name="أمر الشراء المرجعي")

    # قيمة الخصم
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              verbose_name="نسبة الخصم")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          verbose_name="مبلغ الخصم")
    base_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                      verbose_name="المبلغ الأساسي")

    # شروط الخصم
    minimum_quantity = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True,
                                           verbose_name="الحد الأدنى للكمية")
    minimum_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                         verbose_name="الحد الأدنى للمبلغ")
    payment_days = models.IntegerField(null=True, blank=True,
                                       verbose_name="أيام الدفع المبكر")

    # الحالة
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'في الانتظار'),
        ('APPROVED', 'معتمد'),
        ('APPLIED', 'مطبق'),
        ('REJECTED', 'مرفوض'),
        ('EXPIRED', 'منتهي'),
    ], default='PENDING', verbose_name="الحالة")

    # تواريخ
    valid_from = models.DateField(verbose_name="صالح من")
    valid_until = models.DateField(null=True, blank=True, verbose_name="صالح حتى")
    applied_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التطبيق")

    description = models.TextField(blank=True, verbose_name="الوصف")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "خصم مكتسب"
        verbose_name_plural = "الخصومات المكتسبة"
        ordering = ['-date', '-id']

    def save(self, *args, **kwargs):
        # حساب مبلغ الخصم إذا تم تحديد النسبة
        if self.discount_percentage > 0 and self.base_amount > 0:
            self.discount_amount = self.base_amount * (self.discount_percentage / Decimal('100'))
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """التحقق من انتهاء صلاحية الخصم"""
        if self.valid_until:
            from django.utils import timezone
            return timezone.now().date() > self.valid_until
        return False

    @property
    def days_until_expiry(self):
        """عدد الأيام المتبقية حتى انتهاء الصلاحية"""
        if self.valid_until and not self.is_expired:
            from django.utils import timezone
            return (self.valid_until - timezone.now().date()).days
        return 0

    def __str__(self):
        return f"{self.discount_number} - {self.supplier.name} - {self.discount_amount} ر.س"


class EarnedDiscountItem(BaseModel):
    """أصناف الخصم المكتسب"""
    discount = models.ForeignKey(EarnedDiscount, on_delete=models.CASCADE,
                                 related_name="items", verbose_name="الخصم")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="تكلفة الوحدة")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              verbose_name="نسبة الخصم")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          verbose_name="مبلغ الخصم")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")

    class Meta:
        verbose_name = "صنف خصم مكتسب"
        verbose_name_plural = "أصناف الخصومات المكتسبة"

    def save(self, *args, **kwargs):
        # حساب المبالغ
        base_amount = self.quantity * self.unit_cost
        self.discount_amount = base_amount * (self.discount_percentage / Decimal('100'))
        self.total_amount = base_amount - self.discount_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class EarnedDiscount(BaseModel):
    """الخصم المكتسب"""
    DISCOUNT_TYPE_CHOICES = [
        ('VOLUME', 'خصم الكمية'),
        ('PAYMENT_TERMS', 'خصم شروط الدفع'),
        ('SEASONAL', 'خصم موسمي'),
        ('LOYALTY', 'خصم الولاء'),
        ('PROMOTIONAL', 'خصم ترويجي'),
        ('EARLY_PAYMENT', 'خصم الدفع المبكر'),
        ('BULK_ORDER', 'خصم الطلبات الكبيرة'),
        ('OTHER', 'أخرى'),
    ]

    discount_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الخصم")
    date = models.DateField(verbose_name="التاريخ")
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name="المورد")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES,
                                     verbose_name="نوع الخصم")

    # مرجع الخصم (فاتورة أو أمر شراء)
    reference_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.PROTECT,
                                          null=True, blank=True,
                                          verbose_name="الفاتورة المرجعية")
    reference_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT,
                                        null=True, blank=True,
                                        verbose_name="أمر الشراء المرجعي")

    # قيمة الخصم
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              verbose_name="نسبة الخصم")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          verbose_name="مبلغ الخصم")
    base_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                      verbose_name="المبلغ الأساسي")

    # شروط الخصم
    minimum_quantity = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True,
                                           verbose_name="الحد الأدنى للكمية")
    minimum_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                         verbose_name="الحد الأدنى للمبلغ")
    payment_days = models.IntegerField(null=True, blank=True,
                                       verbose_name="أيام الدفع المبكر")

    # الحالة
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'في الانتظار'),
        ('APPROVED', 'معتمد'),
        ('APPLIED', 'مطبق'),
        ('REJECTED', 'مرفوض'),
        ('EXPIRED', 'منتهي'),
    ], default='PENDING', verbose_name="الحالة")

    # تواريخ
    valid_from = models.DateField(verbose_name="صالح من")
    valid_until = models.DateField(null=True, blank=True, verbose_name="صالح حتى")
    applied_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التطبيق")

    description = models.TextField(blank=True, verbose_name="الوصف")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "خصم مكتسب"
        verbose_name_plural = "الخصومات المكتسبة"
        ordering = ['-date', '-id']

    def save(self, *args, **kwargs):
        # حساب مبلغ الخصم إذا تم تحديد النسبة
        if self.discount_percentage > 0 and self.base_amount > 0:
            self.discount_amount = self.base_amount * (self.discount_percentage / Decimal('100'))
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """التحقق من انتهاء صلاحية الخصم"""
        if self.valid_until:
            from django.utils import timezone
            return timezone.now().date() > self.valid_until
        return False

    @property
    def days_until_expiry(self):
        """عدد الأيام المتبقية حتى انتهاء الصلاحية"""
        if self.valid_until and not self.is_expired:
            from django.utils import timezone
            return (self.valid_until - timezone.now().date()).days
        return 0

    def __str__(self):
        return f"{self.discount_number} - {self.supplier.name} - {self.discount_amount} ر.س"


class EarnedDiscountItem(BaseModel):
    """أصناف الخصم المكتسب"""
    discount = models.ForeignKey(EarnedDiscount, on_delete=models.CASCADE,
                                 related_name="items", verbose_name="الخصم")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="تكلفة الوحدة")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              verbose_name="نسبة الخصم")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          verbose_name="مبلغ الخصم")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")

    class Meta:
        verbose_name = "صنف خصم مكتسب"
        verbose_name_plural = "أصناف الخصومات المكتسبة"

    def save(self, *args, **kwargs):
        # حساب المبالغ
        base_amount = self.quantity * self.unit_cost
        self.discount_amount = base_amount * (self.discount_percentage / Decimal('100'))
        self.total_amount = base_amount - self.discount_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"
