from django.db import models
from django.contrib.auth.models import User
from definitions.models import BaseModel, AssetGroup, Treasury
from decimal import Decimal


class Asset(BaseModel):
    """الأصول الثابتة"""

    ASSET_STATUS_CHOICES = [
        ('ACTIVE', 'نشط'),
        ('UNDER_MAINTENANCE', 'تحت الصيانة'),
        ('DISPOSED', 'مستبعد'),
        ('SOLD', 'مباع'),
    ]

    DEPRECIATION_METHOD_CHOICES = [
        ('STRAIGHT_LINE', 'القسط الثابت'),
        ('DECLINING_BALANCE', 'الرصيد المتناقص'),
        ('UNITS_OF_PRODUCTION', 'وحدات الإنتاج'),
        ('SUM_OF_YEARS', 'مجموع سنوات الاستخدام'),
    ]

    # معلومات أساسية
    asset_code = models.CharField(max_length=50, unique=True, verbose_name="كود الأصل")
    name = models.CharField(max_length=200, verbose_name="اسم الأصل")
    description = models.TextField(blank=True, verbose_name="الوصف")
    asset_group = models.ForeignKey(AssetGroup, on_delete=models.PROTECT, verbose_name="مجموعة الأصل")

    # معلومات الشراء
    purchase_date = models.DateField(verbose_name="تاريخ الشراء")
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="تكلفة الشراء")
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="سعر الشراء")
    supplier = models.CharField(max_length=200, blank=True, verbose_name="المورد")
    invoice_number = models.CharField(max_length=100, blank=True, verbose_name="رقم الفاتورة")

    # معلومات الإهلاك
    depreciation_method = models.CharField(
        max_length=20,
        choices=DEPRECIATION_METHOD_CHOICES,
        default='STRAIGHT_LINE',
        verbose_name="طريقة الإهلاك"
    )
    useful_life_years = models.IntegerField(verbose_name="العمر الإنتاجي (سنوات)")
    salvage_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="القيمة التخريدية"
    )
    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="معدل الإهلاك (%)"
    )

    # الحالة والموقع
    status = models.CharField(
        max_length=20,
        choices=ASSET_STATUS_CHOICES,
        default='ACTIVE',
        verbose_name="الحالة"
    )
    location = models.CharField(max_length=200, blank=True, verbose_name="الموقع")
    responsible_person = models.CharField(max_length=200, blank=True, verbose_name="الشخص المسؤول")

    # معلومات إضافية
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="الرقم التسلسلي")
    model = models.CharField(max_length=100, blank=True, verbose_name="الموديل")
    manufacturer = models.CharField(max_length=200, blank=True, verbose_name="الشركة المصنعة")
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name="انتهاء الضمان")

    # القيم المحاسبية
    accumulated_depreciation = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="مجمع الإهلاك"
    )
    book_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="القيمة الدفترية"
    )

    # معلومات البيع (إذا تم بيع الأصل)
    sale_date = models.DateField(null=True, blank=True, verbose_name="تاريخ البيع")
    sale_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="سعر البيع"
    )

    class Meta:
        verbose_name = "أصل ثابت"
        verbose_name_plural = "الأصول الثابتة"
        ordering = ['-purchase_date', 'asset_code']

    def __str__(self):
        return f"{self.asset_code} - {self.name}"

    def save(self, *args, **kwargs):
        # تعيين سعر الشراء إذا لم يتم تحديده
        if not self.purchase_price:
            self.purchase_price = self.purchase_cost
        # حساب القيمة الدفترية
        self.book_value = self.purchase_price - self.accumulated_depreciation
        super().save(*args, **kwargs)

    def calculate_annual_depreciation(self):
        """حساب الإهلاك السنوي"""
        if self.depreciation_method == 'STRAIGHT_LINE':
            return (self.purchase_price - self.salvage_value) / self.useful_life_years
        elif self.depreciation_method == 'DECLINING_BALANCE' and self.depreciation_rate:
            return self.book_value * (self.depreciation_rate / 100)
        return Decimal('0.00')


class AssetPurchase(BaseModel):
    """شراء الأصول"""

    purchase_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الشراء")
    purchase_date = models.DateField(verbose_name="تاريخ الشراء")
    supplier = models.CharField(max_length=200, verbose_name="المورد")
    invoice_number = models.CharField(max_length=100, blank=True, verbose_name="رقم الفاتورة")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="إجمالي المبلغ")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "شراء أصل"
        verbose_name_plural = "مشتريات الأصول"
        ordering = ['-purchase_date', '-id']

    def __str__(self):
        return f"{self.purchase_number} - {self.supplier}"


class AssetPurchaseItem(BaseModel):
    """عناصر شراء الأصول"""

    purchase = models.ForeignKey(AssetPurchase, on_delete=models.CASCADE, related_name='items')
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, verbose_name="الأصل")
    quantity = models.IntegerField(default=1, verbose_name="الكمية")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="تكلفة الوحدة")
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="إجمالي التكلفة")

    class Meta:
        verbose_name = "عنصر شراء أصل"
        verbose_name_plural = "عناصر شراء الأصول"

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


class AssetRenewal(BaseModel):
    """تجديد الأصول"""

    RENEWAL_TYPE_CHOICES = [
        ('MAINTENANCE', 'صيانة'),
        ('UPGRADE', 'ترقية'),
        ('REPAIR', 'إصلاح'),
        ('REPLACEMENT', 'استبدال جزء'),
    ]

    renewal_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التجديد")
    renewal_date = models.DateField(verbose_name="تاريخ التجديد")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, verbose_name="الأصل")
    renewal_type = models.CharField(max_length=20, choices=RENEWAL_TYPE_CHOICES, verbose_name="نوع التجديد")
    description = models.TextField(verbose_name="وصف التجديد")
    cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="التكلفة")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    supplier = models.CharField(max_length=200, blank=True, verbose_name="المورد/المقاول")
    invoice_number = models.CharField(max_length=100, blank=True, verbose_name="رقم الفاتورة")
    extends_useful_life = models.BooleanField(default=False, verbose_name="يمدد العمر الإنتاجي")
    additional_years = models.IntegerField(default=0, verbose_name="سنوات إضافية")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "تجديد أصل"
        verbose_name_plural = "تجديدات الأصول"
        ordering = ['-renewal_date', '-id']

    def __str__(self):
        return f"{self.renewal_number} - {self.asset.name}"


class AssetSale(BaseModel):
    """بيع الأصول"""

    sale_number = models.CharField(max_length=50, unique=True, verbose_name="رقم البيع")
    sale_date = models.DateField(verbose_name="تاريخ البيع")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, verbose_name="الأصل")
    buyer = models.CharField(max_length=200, verbose_name="المشتري")
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="سعر البيع")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")

    # القيم المحاسبية وقت البيع
    book_value_at_sale = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="القيمة الدفترية وقت البيع")
    gain_loss_on_sale = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="ربح/خسارة البيع")

    invoice_number = models.CharField(max_length=100, blank=True, verbose_name="رقم الفاتورة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "بيع أصل"
        verbose_name_plural = "مبيعات الأصول"
        ordering = ['-sale_date', '-id']

    def __str__(self):
        return f"{self.sale_number} - {self.asset.name}"

    def save(self, *args, **kwargs):
        # حساب ربح أو خسارة البيع
        self.gain_loss_on_sale = self.sale_price - self.book_value_at_sale
        super().save(*args, **kwargs)


class DepreciationEntry(BaseModel):
    """قيود الإهلاك"""

    entry_number = models.CharField(max_length=50, unique=True, verbose_name="رقم القيد")
    entry_date = models.DateField(verbose_name="تاريخ القيد")
    period_year = models.IntegerField(verbose_name="السنة")
    period_month = models.IntegerField(verbose_name="الشهر")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, verbose_name="الأصل")
    depreciation_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مبلغ الإهلاك")
    accumulated_depreciation_before = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مجمع الإهلاك قبل")
    accumulated_depreciation_after = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مجمع الإهلاك بعد")
    book_value_after = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="القيمة الدفترية بعد")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "قيد إهلاك"
        verbose_name_plural = "قيود الإهلاك"
        ordering = ['-entry_date', '-id']
        unique_together = ['asset', 'period_year', 'period_month']

    def __str__(self):
        return f"{self.entry_number} - {self.asset.name} ({self.period_month}/{self.period_year})"


class AssetMaintenance(BaseModel):
    """صيانة الأصول"""

    MAINTENANCE_TYPE_CHOICES = [
        ('PREVENTIVE', 'صيانة وقائية'),
        ('CORRECTIVE', 'صيانة تصحيحية'),
        ('EMERGENCY', 'صيانة طارئة'),
        ('SCHEDULED', 'صيانة مجدولة'),
    ]

    maintenance_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الصيانة")
    maintenance_date = models.DateField(verbose_name="تاريخ الصيانة")
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, verbose_name="الأصل")
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES, verbose_name="نوع الصيانة")
    description = models.TextField(verbose_name="وصف الصيانة")
    cost = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="التكلفة")
    treasury = models.ForeignKey(Treasury, on_delete=models.PROTECT, verbose_name="الخزينة")
    technician = models.CharField(max_length=200, blank=True, verbose_name="الفني")
    supplier = models.CharField(max_length=200, blank=True, verbose_name="المورد")
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    next_maintenance_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الصيانة القادمة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "صيانة أصل"
        verbose_name_plural = "صيانة الأصول"
        ordering = ['-maintenance_date', '-id']

    def __str__(self):
        return f"{self.maintenance_number} - {self.asset.name}"
