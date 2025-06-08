from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from definitions.models import BaseModel, Item, Warehouse, Currency, Person
from decimal import Decimal


class Customer(BaseModel):
    """العملاء"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود العميل")
    name = models.CharField(max_length=200, verbose_name="اسم العميل")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="الشخص المسؤول")
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    address = models.TextField(blank=True, verbose_name="العنوان")
    tax_number = models.CharField(max_length=50, blank=True, verbose_name="الرقم الضريبي")
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="حد الائتمان")
    payment_terms = models.IntegerField(default=0, verbose_name="شروط الدفع (أيام)")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              verbose_name="نسبة الخصم")

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class SalesInvoice(BaseModel):
    """فواتير المبيعات"""
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة")
    date = models.DateField(verbose_name="التاريخ")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="العميل")
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
        ('DELIVERED', 'مسلمة'),
        ('PAID', 'مدفوعة'),
        ('CANCELLED', 'ملغية'),
    ], default='DRAFT', verbose_name="الحالة")

    due_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الاستحقاق")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    salesperson = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="sales_invoices", verbose_name="مندوب المبيعات")

    class Meta:
        verbose_name = "فاتورة مبيعات"
        verbose_name_plural = "فواتير المبيعات"
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
        return f"{self.invoice_number} - {self.customer.name}"


class SalesInvoiceItem(BaseModel):
    """أصناف فواتير المبيعات"""
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE,
                                related_name="items", verbose_name="الفاتورة")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="سعر الوحدة")
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

    class Meta:
        verbose_name = "صنف فاتورة مبيعات"
        verbose_name_plural = "أصناف فواتير المبيعات"

    def save(self, *args, **kwargs):
        # حساب المبالغ
        subtotal = self.quantity * self.unit_price
        self.discount_amount = subtotal * (self.discount_percentage / Decimal('100'))
        amount_after_discount = subtotal - self.discount_amount
        self.tax_amount = amount_after_discount * (self.tax_percentage / Decimal('100'))
        self.total_amount = amount_after_discount + self.tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class SalesReturn(BaseModel):
    """مرتجعات المبيعات"""
    return_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المرتجع")
    date = models.DateField(verbose_name="التاريخ")
    original_invoice = models.ForeignKey(SalesInvoice, on_delete=models.PROTECT,
                                         null=True, blank=True,
                                         verbose_name="الفاتورة الأصلية")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="العميل")
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
        verbose_name = "مرتجع مبيعات"
        verbose_name_plural = "مرتجعات المبيعات"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.return_number} - {self.customer.name}"


class SalesReturnItem(BaseModel):
    """أصناف مرتجعات المبيعات"""
    return_doc = models.ForeignKey(SalesReturn, on_delete=models.CASCADE,
                                   related_name="items", verbose_name="المرتجع")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="سعر الوحدة")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")

    class Meta:
        verbose_name = "صنف مرتجع مبيعات"
        verbose_name_plural = "أصناف مرتجعات المبيعات"

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class PriceList(BaseModel):
    """قوائم الأسعار"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود قائمة الأسعار")
    name = models.CharField(max_length=100, verbose_name="اسم قائمة الأسعار")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # فترة الصلاحية
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ النهاية")

    # إعدادات
    is_default = models.BooleanField(default=False, verbose_name="قائمة افتراضية")
    currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, verbose_name="العملة"
    )

    # نوع القائمة
    price_type = models.CharField(max_length=20, choices=[
        ('RETAIL', 'تجزئة'),
        ('WHOLESALE', 'جملة'),
        ('SPECIAL', 'خاص'),
        ('PROMOTIONAL', 'ترويجي'),
    ], default='RETAIL', verbose_name="نوع القائمة")

    class Meta:
        verbose_name = "قائمة أسعار"
        verbose_name_plural = "قوائم الأسعار"
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')

    def save(self, *args, **kwargs):
        # تعيين العملة الافتراضية إذا لم تكن محددة
        if not self.currency_id:
            try:
                from definitions.models import Currency
                default_currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
                if default_currency:
                    self.currency = default_currency
            except:
                pass

        if self.is_default:
            PriceList.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """هل قائمة الأسعار نشطة"""
        today = timezone.now().date()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today


class PriceListItem(BaseModel):
    """عناصر قائمة الأسعار"""
    price_list = models.ForeignKey(
        PriceList, on_delete=models.CASCADE,
        related_name='items', verbose_name="قائمة الأسعار"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="الصنف"
    )

    # الأسعار
    unit_price = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="سعر الوحدة"
    )
    min_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=1,
        verbose_name="الحد الأدنى للكمية"
    )
    max_discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="أقصى نسبة خصم مسموحة (%)"
    )

    class Meta:
        verbose_name = "عنصر قائمة أسعار"
        verbose_name_plural = "عناصر قوائم الأسعار"
        unique_together = ['price_list', 'item']

    def __str__(self):
        return f"{self.price_list.name} - {self.item.name}"


class Quotation(BaseModel):
    """عروض الأسعار"""
    quotation_number = models.CharField(max_length=50, unique=True, verbose_name="رقم عرض السعر")
    date = models.DateField(verbose_name="التاريخ")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name="العميل")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="العملة")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000,
                                        verbose_name="سعر الصرف")

    # فترة الصلاحية
    valid_until = models.DateField(verbose_name="صالح حتى")

    # المبالغ
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                   verbose_name="المجموع الفرعي")
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          verbose_name="مبلغ الخصم")
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="مبلغ الضريبة")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                       verbose_name="إجمالي المبلغ")

    # الحالة
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('SENT', 'مرسل'),
        ('ACCEPTED', 'مقبول'),
        ('REJECTED', 'مرفوض'),
        ('EXPIRED', 'منتهي الصلاحية'),
        ('CONVERTED', 'تم تحويله لفاتورة'),
    ], default='DRAFT', verbose_name="الحالة")

    # شروط وأحكام
    terms_and_conditions = models.TextField(blank=True, verbose_name="الشروط والأحكام")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    salesperson = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="quotations", verbose_name="مندوب المبيعات")

    class Meta:
        verbose_name = "عرض سعر"
        verbose_name_plural = "عروض الأسعار"
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

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quotation_number} - {self.customer.name}"

    @property
    def is_expired(self):
        """هل عرض السعر منتهي الصلاحية"""
        return timezone.now().date() > self.valid_until

    @property
    def days_until_expiry(self):
        """عدد الأيام حتى انتهاء الصلاحية"""
        today = timezone.now().date()
        if self.valid_until > today:
            return (self.valid_until - today).days
        return 0


class QuotationItem(BaseModel):
    """أصناف عروض الأسعار"""
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE,
                                  related_name="items", verbose_name="عرض السعر")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="سعر الوحدة")
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

    # معلومات إضافية
    description = models.TextField(blank=True, verbose_name="الوصف")
    delivery_time = models.CharField(max_length=100, blank=True, verbose_name="مدة التسليم")

    class Meta:
        verbose_name = "صنف عرض سعر"
        verbose_name_plural = "أصناف عروض الأسعار"

    def save(self, *args, **kwargs):
        # حساب المبالغ
        subtotal = self.quantity * self.unit_price
        self.discount_amount = subtotal * (self.discount_percentage / Decimal('100'))
        amount_after_discount = subtotal - self.discount_amount
        self.tax_amount = amount_after_discount * (self.tax_percentage / Decimal('100'))
        self.total_amount = amount_after_discount + self.tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"


class DiscountPolicy(BaseModel):
    """سياسات الخصم"""
    name = models.CharField(max_length=100, verbose_name="اسم السياسة")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # نوع الخصم
    discount_type = models.CharField(max_length=20, choices=[
        ('PERCENTAGE', 'نسبة مئوية'),
        ('FIXED_AMOUNT', 'مبلغ ثابت'),
        ('QUANTITY_BASED', 'حسب الكمية'),
        ('CUSTOMER_TYPE', 'حسب نوع العميل'),
    ], verbose_name="نوع الخصم")

    # قيم الخصم
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="نسبة الخصم (%)"
    )
    discount_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="مبلغ الخصم"
    )

    # شروط التطبيق
    min_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأدنى للكمية"
    )
    min_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأدنى للمبلغ"
    )

    # فترة الصلاحية
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ النهاية")

    # العملاء المستهدفون
    applicable_customers = models.ManyToManyField(
        Customer, blank=True, verbose_name="العملاء المستهدفون"
    )

    # الأصناف المستهدفة
    applicable_items = models.ManyToManyField(
        Item, blank=True, verbose_name="الأصناف المستهدفة"
    )

    class Meta:
        verbose_name = "سياسة خصم"
        verbose_name_plural = "سياسات الخصم"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        """هل السياسة نشطة"""
        today = timezone.now().date()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today
