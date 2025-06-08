from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import os


class BaseModel(models.Model):
    """نموذج أساسي يحتوي على الحقول المشتركة"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="%(class)s_created", verbose_name="أنشئ بواسطة")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="%(class)s_updated", verbose_name="حُدث بواسطة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    class Meta:
        abstract = True


class Currency(BaseModel):
    """العملات"""
    code = models.CharField(max_length=3, unique=True, verbose_name="رمز العملة")
    name = models.CharField(max_length=100, verbose_name="اسم العملة")
    symbol = models.CharField(max_length=10, verbose_name="رمز العملة")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000,
                                        verbose_name="سعر الصرف")
    is_base_currency = models.BooleanField(default=False, verbose_name="العملة الأساسية")

    class Meta:
        verbose_name = "عملة"
        verbose_name_plural = "العملات"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class EgyptianBankRate(BaseModel):
    """أسعار العملات في البنوك المصرية"""
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, verbose_name="العملة")
    bank_name = models.CharField(max_length=100, verbose_name="اسم البنك")
    buy_rate = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="سعر الشراء")
    sell_rate = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="سعر البيع")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    # معلومات إضافية
    source_url = models.URLField(blank=True, verbose_name="مصدر البيانات")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "سعر صرف البنك"
        verbose_name_plural = "أسعار صرف البنوك"
        unique_together = ['currency', 'bank_name']
        ordering = ['bank_name', 'currency__code']

    @property
    def average_rate(self):
        """متوسط سعر الشراء والبيع"""
        return (self.buy_rate + self.sell_rate) / 2

    @property
    def spread(self):
        """الفرق بين سعر البيع والشراء"""
        return self.sell_rate - self.buy_rate

    @property
    def spread_percentage(self):
        """نسبة الفرق"""
        if self.buy_rate > 0:
            return (self.spread / self.buy_rate) * 100
        return 0

    def __str__(self):
        return f"{self.bank_name} - {self.currency.code}"


class CurrencyRateHistory(BaseModel):
    """تاريخ أسعار العملات"""
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, verbose_name="العملة")
    rate = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="السعر")
    rate_type = models.CharField(max_length=20, choices=[
        ('BUY', 'شراء'),
        ('SELL', 'بيع'),
        ('AVERAGE', 'متوسط'),
        ('OFFICIAL', 'رسمي'),
    ], default='AVERAGE', verbose_name="نوع السعر")
    source = models.CharField(max_length=100, verbose_name="المصدر")
    recorded_date = models.DateTimeField(verbose_name="تاريخ التسجيل")

    class Meta:
        verbose_name = "تاريخ سعر العملة"
        verbose_name_plural = "تاريخ أسعار العملات"
        ordering = ['-recorded_date']

    def __str__(self):
        return f"{self.currency.code} - {self.rate} - {self.recorded_date.strftime('%Y-%m-%d %H:%M')}"


class Warehouse(BaseModel):
    """المخازن"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود المخزن")
    name = models.CharField(max_length=100, verbose_name="اسم المخزن")
    location = models.TextField(blank=True, verbose_name="الموقع")
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="managed_warehouses", verbose_name="مدير المخزن")
    capacity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                   verbose_name="السعة")

    class Meta:
        verbose_name = "مخزن"
        verbose_name_plural = "المخازن"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class ItemCategory(BaseModel):
    """فئات الأصناف"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود الفئة")
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               related_name="children", verbose_name="الفئة الأب")
    description = models.TextField(blank=True, verbose_name="الوصف")

    class Meta:
        verbose_name = "فئة صنف"
        verbose_name_plural = "فئات الأصناف"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Unit(BaseModel):
    """وحدات القياس"""
    code = models.CharField(max_length=10, unique=True, verbose_name="كود الوحدة")
    name = models.CharField(max_length=50, verbose_name="اسم الوحدة")
    symbol = models.CharField(max_length=10, verbose_name="رمز الوحدة")

    class Meta:
        verbose_name = "وحدة قياس"
        verbose_name_plural = "وحدات القياس"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Item(BaseModel):
    """الأصناف"""
    code = models.CharField(max_length=50, unique=True, verbose_name="كود الصنف")
    name = models.CharField(max_length=200, verbose_name="اسم الصنف")
    category = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True,
                                 verbose_name="الفئة")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="وحدة القياس")
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True,
                               verbose_name="الباركود")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # معلومات التكلفة والسعر
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="سعر التكلفة")
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                        verbose_name="سعر البيع")

    # حدود المخزون
    min_stock = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="الحد الأدنى للمخزون")
    max_stock = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="الحد الأقصى للمخزون")

    # معلومات إضافية
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True,
                                 verbose_name="الوزن")
    dimensions = models.CharField(max_length=100, blank=True, verbose_name="الأبعاد")
    image = models.ImageField(upload_to='items/', blank=True, null=True,
                              verbose_name="صورة الصنف")

    class Meta:
        verbose_name = "صنف"
        verbose_name_plural = "الأصناف"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Bank(BaseModel):
    """البنوك"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود البنك")
    name = models.CharField(max_length=100, verbose_name="اسم البنك")
    branch = models.CharField(max_length=100, blank=True, verbose_name="الفرع")
    account_number = models.CharField(max_length=50, verbose_name="رقم الحساب")
    account_name = models.CharField(max_length=100, verbose_name="اسم الحساب")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="العملة")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                  verbose_name="الرصيد")
    contact_info = models.TextField(blank=True, verbose_name="معلومات الاتصال")

    class Meta:
        verbose_name = "بنك"
        verbose_name_plural = "البنوك"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.account_number}"

    def save(self, *args, **kwargs):
        # تعيين العملة الافتراضية إذا لم تكن محددة
        if not self.currency_id:
            try:
                default_currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
                if default_currency:
                    self.currency = default_currency
            except:
                pass

        super().save(*args, **kwargs)


class Treasury(BaseModel):
    """الخزائن"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود الخزينة")
    name = models.CharField(max_length=100, verbose_name="اسم الخزينة")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="العملة")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                  verbose_name="الرصيد")
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                           blank=True, related_name="managed_treasuries",
                                           verbose_name="المسؤول")
    location = models.CharField(max_length=200, blank=True, verbose_name="الموقع")

    class Meta:
        verbose_name = "خزينة"
        verbose_name_plural = "الخزائن"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        # تعيين العملة الافتراضية إذا لم تكن محددة
        if not self.currency_id:
            try:
                default_currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
                if default_currency:
                    self.currency = default_currency
            except:
                pass

        super().save(*args, **kwargs)


class WarehouseZone(BaseModel):
    """مناطق المخزن"""
    code = models.CharField(max_length=20, verbose_name="كود المنطقة")
    name = models.CharField(max_length=100, verbose_name="اسم المنطقة")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="المخزن")
    description = models.TextField(blank=True, verbose_name="الوصف")
    temperature_controlled = models.BooleanField(default=False, verbose_name="مكيف الهواء")
    humidity_controlled = models.BooleanField(default=False, verbose_name="مراقب الرطوبة")
    security_level = models.CharField(max_length=20, choices=[
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('CRITICAL', 'حرج'),
    ], default='MEDIUM', verbose_name="مستوى الأمان")

    class Meta:
        verbose_name = "منطقة مخزن"
        verbose_name_plural = "مناطق المخازن"
        ordering = ['warehouse', 'name']
        unique_together = ['warehouse', 'code']

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"


class WarehouseLocation(BaseModel):
    """مواقع الأصناف في المخزن"""
    code = models.CharField(max_length=30, verbose_name="كود الموقع")
    name = models.CharField(max_length=100, verbose_name="اسم الموقع")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="المخزن")
    zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name="المنطقة")

    # تفاصيل الموقع
    aisle = models.CharField(max_length=10, blank=True, verbose_name="الممر")
    rack = models.CharField(max_length=10, blank=True, verbose_name="الرف")
    shelf = models.CharField(max_length=10, blank=True, verbose_name="الطبقة")
    bin = models.CharField(max_length=10, blank=True, verbose_name="الصندوق")

    # خصائص الموقع
    capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                   verbose_name="السعة")
    capacity_unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True,
                                      verbose_name="وحدة السعة")
    max_weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True,
                                     verbose_name="الحد الأقصى للوزن (كجم)")

    # حالة الموقع
    is_available = models.BooleanField(default=True, verbose_name="متاح")
    is_pickable = models.BooleanField(default=True, verbose_name="قابل للانتقاء")
    is_receivable = models.BooleanField(default=True, verbose_name="قابل للاستقبال")

    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "موقع مخزن"
        verbose_name_plural = "مواقع المخازن"
        ordering = ['warehouse', 'aisle', 'rack', 'shelf', 'bin']
        unique_together = ['warehouse', 'code']

    def __str__(self):
        location_parts = []
        if self.aisle:
            location_parts.append(f"ممر {self.aisle}")
        if self.rack:
            location_parts.append(f"رف {self.rack}")
        if self.shelf:
            location_parts.append(f"طبقة {self.shelf}")
        if self.bin:
            location_parts.append(f"صندوق {self.bin}")

        location_str = " - ".join(location_parts) if location_parts else self.name
        return f"{self.warehouse.name}: {location_str}"

    @property
    def full_location_code(self):
        """الكود الكامل للموقع"""
        parts = [self.warehouse.code]
        if self.zone:
            parts.append(self.zone.code)
        if self.aisle:
            parts.append(self.aisle)
        if self.rack:
            parts.append(self.rack)
        if self.shelf:
            parts.append(self.shelf)
        if self.bin:
            parts.append(self.bin)
        return "-".join(parts)


class ItemLocation(BaseModel):
    """مواقع الأصناف في المخازن"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="الصنف")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name="المخزن")
    location = models.ForeignKey(WarehouseLocation, on_delete=models.CASCADE, verbose_name="الموقع")

    # حدود المخزون لهذا الموقع
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                       verbose_name="الحد الأدنى")
    max_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       verbose_name="الحد الأقصى")
    reorder_point = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                        verbose_name="نقطة إعادة الطلب")

    # أولوية الموقع للصنف
    priority = models.IntegerField(default=1, verbose_name="الأولوية")

    # نوع الموقع
    location_type = models.CharField(max_length=20, choices=[
        ('PRIMARY', 'أساسي'),
        ('SECONDARY', 'ثانوي'),
        ('OVERFLOW', 'فائض'),
        ('PICKING', 'انتقاء'),
        ('RESERVE', 'احتياطي'),
    ], default='PRIMARY', verbose_name="نوع الموقع")

    # حالة الموقع للصنف
    is_default = models.BooleanField(default=False, verbose_name="الموقع الافتراضي")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    # تواريخ
    assigned_date = models.DateField(auto_now_add=True, verbose_name="تاريخ التخصيص")
    last_movement_date = models.DateTimeField(null=True, blank=True, verbose_name="آخر حركة")

    class Meta:
        verbose_name = "موقع صنف"
        verbose_name_plural = "مواقع الأصناف"
        ordering = ['item', 'warehouse', 'priority']
        unique_together = ['item', 'warehouse', 'location']

    def __str__(self):
        return f"{self.item.name} - {self.location}"

    def clean(self):
        from django.core.exceptions import ValidationError

        # التأكد من أن الموقع في نفس المخزن
        if self.location.warehouse != self.warehouse:
            raise ValidationError('الموقع يجب أن يكون في نفس المخزن')

        # التأكد من أن الحد الأقصى أكبر من الحد الأدنى
        if self.max_quantity and self.min_quantity and self.max_quantity <= self.min_quantity:
            raise ValidationError('الحد الأقصى يجب أن يكون أكبر من الحد الأدنى')

    def save(self, *args, **kwargs):
        self.clean()

        # إذا كان هذا الموقع افتراضي، قم بإلغاء الافتراضية من المواقع الأخرى
        if self.is_default:
            ItemLocation.objects.filter(
                item=self.item,
                warehouse=self.warehouse,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)


class AssetGroup(BaseModel):
    """مجموعات الأصول"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود المجموعة")
    name = models.CharField(max_length=100, verbose_name="اسم المجموعة")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="المجموعة الأب")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # إعدادات الاستهلاك
    depreciation_method = models.CharField(max_length=20, choices=[
        ('STRAIGHT_LINE', 'القسط الثابت'),
        ('DECLINING_BALANCE', 'الرصيد المتناقص'),
        ('UNITS_OF_PRODUCTION', 'وحدات الإنتاج'),
        ('SUM_OF_YEARS', 'مجموع سنوات الخدمة'),
    ], default='STRAIGHT_LINE', verbose_name="طريقة الاستهلاك")

    default_useful_life = models.IntegerField(null=True, blank=True, verbose_name="العمر الافتراضي (سنوات)")
    default_salvage_value_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="نسبة القيمة المتبقية (%)"
    )

    # الحسابات المحاسبية
    asset_account = models.CharField(max_length=20, blank=True, verbose_name="حساب الأصل")
    depreciation_account = models.CharField(max_length=20, blank=True, verbose_name="حساب الاستهلاك")
    accumulated_depreciation_account = models.CharField(
        max_length=20, blank=True, verbose_name="حساب مجمع الاستهلاك"
    )

    # إعدادات إضافية
    requires_insurance = models.BooleanField(default=False, verbose_name="يتطلب تأمين")
    requires_maintenance = models.BooleanField(default=True, verbose_name="يتطلب صيانة")
    is_depreciable = models.BooleanField(default=True, verbose_name="قابل للاستهلاك")

    # فئة الأصل
    asset_category = models.CharField(max_length=20, choices=[
        ('BUILDING', 'مباني'),
        ('MACHINERY', 'آلات ومعدات'),
        ('VEHICLE', 'مركبات'),
        ('FURNITURE', 'أثاث ومفروشات'),
        ('COMPUTER', 'أجهزة حاسوب'),
        ('LAND', 'أراضي'),
        ('INTANGIBLE', 'أصول معنوية'),
        ('OTHER', 'أخرى'),
    ], default='OTHER', verbose_name="فئة الأصل")

    # حدود التكلفة
    min_cost_threshold = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأدنى للتكلفة"
    )
    max_cost_threshold = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأقصى للتكلفة"
    )

    class Meta:
        verbose_name = "مجموعة أصول"
        verbose_name_plural = "مجموعات الأصول"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        from django.core.exceptions import ValidationError

        # التأكد من أن المجموعة الأب ليست نفس المجموعة
        if self.parent == self:
            raise ValidationError('لا يمكن أن تكون المجموعة أب لنفسها')

        # التأكد من عدم وجود دورة في التسلسل الهرمي
        if self.parent:
            current = self.parent
            while current:
                if current == self:
                    raise ValidationError('لا يمكن إنشاء دورة في التسلسل الهرمي')
                current = current.parent

        # التأكد من أن الحد الأقصى أكبر من الحد الأدنى
        if (self.min_cost_threshold and self.max_cost_threshold and
            self.max_cost_threshold <= self.min_cost_threshold):
            raise ValidationError('الحد الأقصى للتكلفة يجب أن يكون أكبر من الحد الأدنى')

        # التأكد من صحة نسبة القيمة المتبقية
        if self.default_salvage_value_rate < 0 or self.default_salvage_value_rate > 100:
            raise ValidationError('نسبة القيمة المتبقية يجب أن تكون بين 0 و 100')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """الاسم الكامل مع التسلسل الهرمي"""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name

    @property
    def level(self):
        """مستوى المجموعة في التسلسل الهرمي"""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level

    def get_children(self):
        """الحصول على المجموعات الفرعية"""
        return AssetGroup.objects.filter(parent=self, is_active=True)

    def get_all_descendants(self):
        """الحصول على جميع المجموعات الفرعية (بما في ذلك الفرعية من الفرعية)"""
        descendants = []
        for child in self.get_children():
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def get_ancestors(self):
        """الحصول على جميع المجموعات الأب"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors


class Person(BaseModel):
    """الأشخاص والجهات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود الشخص/الجهة")
    name = models.CharField(max_length=200, verbose_name="الاسم")
    name_english = models.CharField(max_length=200, blank=True, verbose_name="الاسم بالإنجليزية")

    # نوع الشخص/الجهة
    person_type = models.CharField(max_length=20, choices=[
        ('CUSTOMER', 'عميل'),
        ('SUPPLIER', 'مورد'),
        ('EMPLOYEE', 'موظف'),
        ('BOTH', 'عميل ومورد'),
        ('BANK', 'بنك'),
        ('GOVERNMENT', 'جهة حكومية'),
        ('PARTNER', 'شريك'),
        ('OTHER', 'أخرى'),
    ], default='CUSTOMER', verbose_name="نوع الشخص/الجهة")

    # نوع الكيان
    entity_type = models.CharField(max_length=20, choices=[
        ('INDIVIDUAL', 'فرد'),
        ('COMPANY', 'شركة'),
        ('INSTITUTION', 'مؤسسة'),
        ('GOVERNMENT', 'جهة حكومية'),
    ], default='INDIVIDUAL', verbose_name="نوع الكيان")

    # معلومات الهوية
    national_id = models.CharField(max_length=20, blank=True, verbose_name="رقم الهوية/السجل التجاري")
    tax_number = models.CharField(max_length=20, blank=True, verbose_name="الرقم الضريبي")
    commercial_register = models.CharField(max_length=20, blank=True, verbose_name="السجل التجاري")

    # معلومات الاتصال
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    mobile = models.CharField(max_length=20, blank=True, verbose_name="الجوال")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    website = models.URLField(blank=True, verbose_name="الموقع الإلكتروني")

    # العنوان
    address = models.TextField(blank=True, verbose_name="العنوان")
    city = models.CharField(max_length=100, blank=True, verbose_name="المدينة")
    state = models.CharField(max_length=100, blank=True, verbose_name="المحافظة/المنطقة")
    country = models.CharField(max_length=100, default='مصر', verbose_name="الدولة")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="الرمز البريدي")

    # معلومات مالية
    credit_limit = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="حد الائتمان"
    )
    payment_terms = models.IntegerField(null=True, blank=True, verbose_name="مدة السداد (أيام)")
    currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, null=True, blank=True,
        verbose_name="العملة الافتراضية"
    )

    # الحسابات المحاسبية
    account_receivable = models.CharField(max_length=20, blank=True, verbose_name="حساب المدينين")
    account_payable = models.CharField(max_length=20, blank=True, verbose_name="حساب الدائنين")

    # معلومات إضافية
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="الشخص المسؤول")
    contact_title = models.CharField(max_length=100, blank=True, verbose_name="المنصب")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    # إعدادات
    is_active_customer = models.BooleanField(default=True, verbose_name="عميل نشط")
    is_active_supplier = models.BooleanField(default=False, verbose_name="مورد نشط")
    allow_credit = models.BooleanField(default=True, verbose_name="السماح بالائتمان")

    # تواريخ مهمة
    registration_date = models.DateField(null=True, blank=True, verbose_name="تاريخ التسجيل")
    last_transaction_date = models.DateField(null=True, blank=True, verbose_name="تاريخ آخر معاملة")

    class Meta:
        verbose_name = "شخص/جهة"
        verbose_name_plural = "الأشخاص والجهات"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        # تعيين العملة الافتراضية إذا لم تكن محددة
        if not self.currency_id:
            try:
                default_currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
                if default_currency:
                    self.currency = default_currency
            except:
                pass

        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError

        # التحقق من صحة البريد الإلكتروني
        if self.email:
            from django.core.validators import validate_email
            try:
                validate_email(self.email)
            except:
                raise ValidationError('البريد الإلكتروني غير صحيح')

        # التحقق من حد الائتمان
        if self.credit_limit and self.credit_limit < 0:
            raise ValidationError('حد الائتمان لا يمكن أن يكون سالباً')

        # التحقق من مدة السداد
        if self.payment_terms and self.payment_terms < 0:
            raise ValidationError('مدة السداد لا يمكن أن تكون سالبة')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """العنوان الكامل"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.country:
            address_parts.append(self.country)
        return ', '.join(address_parts)

    @property
    def display_name(self):
        """الاسم للعرض"""
        if self.name_english:
            return f"{self.name} ({self.name_english})"
        return self.name

    @property
    def is_customer(self):
        """هل هو عميل"""
        return self.person_type in ['CUSTOMER', 'BOTH'] and self.is_active_customer

    @property
    def is_supplier(self):
        """هل هو مورد"""
        return self.person_type in ['SUPPLIER', 'BOTH'] and self.is_active_supplier

    def get_balance(self):
        """الحصول على الرصيد (سيتم تطويره لاحقاً مع نظام المحاسبة)"""
        # TODO: حساب الرصيد من الحركات المحاسبية
        return 0

    def get_last_transaction(self):
        """الحصول على آخر معاملة (سيتم تطويره لاحقاً)"""
        # TODO: الحصول على آخر معاملة من قاعدة البيانات
        return None


class ExpenseCategory(BaseModel):
    """فئات المصروفات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود فئة المصروف")
    name = models.CharField(max_length=100, verbose_name="اسم فئة المصروف")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # تصنيف المصروف
    category = models.CharField(max_length=20, choices=[
        ('OPERATIONAL', 'مصروفات تشغيلية'),
        ('ADMINISTRATIVE', 'مصروفات إدارية'),
        ('SELLING', 'مصروفات بيعية'),
        ('FINANCIAL', 'مصروفات مالية'),
        ('CAPITAL', 'مصروفات رأسمالية'),
        ('OTHER', 'أخرى'),
    ], default='OPERATIONAL', verbose_name="تصنيف المصروف")

    # الحساب المحاسبي الافتراضي
    default_account = models.CharField(max_length=20, blank=True, verbose_name="الحساب الافتراضي")

    # إعدادات
    requires_approval = models.BooleanField(default=False, verbose_name="يتطلب موافقة")
    max_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأقصى للمبلغ"
    )

    class Meta:
        verbose_name = "فئة مصروف"
        verbose_name_plural = "فئات المصروفات"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.max_amount and self.max_amount <= 0:
            raise ValidationError('الحد الأقصى للمبلغ يجب أن يكون أكبر من صفر')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ExpenseItem(BaseModel):
    """بنود المصروفات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود بند المصروف")
    name = models.CharField(max_length=100, verbose_name="اسم بند المصروف")
    expense_category = models.ForeignKey(
        ExpenseCategory, on_delete=models.PROTECT, verbose_name="فئة المصروف"
    )
    description = models.TextField(blank=True, verbose_name="الوصف")

    # الحساب المحاسبي
    account_number = models.CharField(max_length=20, blank=True, verbose_name="رقم الحساب")

    # إعدادات المصروف
    is_recurring = models.BooleanField(default=False, verbose_name="مصروف دوري")
    recurring_period = models.CharField(max_length=20, choices=[
        ('DAILY', 'يومي'),
        ('WEEKLY', 'أسبوعي'),
        ('MONTHLY', 'شهري'),
        ('QUARTERLY', 'ربع سنوي'),
        ('YEARLY', 'سنوي'),
    ], blank=True, verbose_name="فترة التكرار")

    # حدود المبلغ
    min_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأدنى للمبلغ"
    )
    max_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأقصى للمبلغ"
    )

    # إعدادات
    requires_document = models.BooleanField(default=True, verbose_name="يتطلب مستند")
    requires_approval = models.BooleanField(default=False, verbose_name="يتطلب موافقة")

    class Meta:
        verbose_name = "بند مصروف"
        verbose_name_plural = "بنود المصروفات"
        ordering = ['expense_category', 'name']

    def __str__(self):
        return f"{self.name} ({self.expense_category.name})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.min_amount and self.min_amount < 0:
            raise ValidationError('الحد الأدنى للمبلغ لا يمكن أن يكون سالباً')

        if self.max_amount and self.max_amount <= 0:
            raise ValidationError('الحد الأقصى للمبلغ يجب أن يكون أكبر من صفر')

        if self.min_amount and self.max_amount and self.min_amount > self.max_amount:
            raise ValidationError('الحد الأدنى للمبلغ لا يمكن أن يكون أكبر من الحد الأقصى')

        if self.is_recurring and not self.recurring_period:
            raise ValidationError('يجب تحديد فترة التكرار للمصروف الدوري')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """الاسم الكامل مع فئة المصروف"""
        return f"{self.expense_category.name} - {self.name}"


class RevenueCategory(BaseModel):
    """فئات الإيرادات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود فئة الإيراد")
    name = models.CharField(max_length=100, verbose_name="اسم فئة الإيراد")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # تصنيف الإيراد
    category = models.CharField(max_length=20, choices=[
        ('SALES', 'إيرادات مبيعات'),
        ('SERVICES', 'إيرادات خدمات'),
        ('INVESTMENT', 'إيرادات استثمارية'),
        ('FINANCIAL', 'إيرادات مالية'),
        ('RENTAL', 'إيرادات إيجارات'),
        ('OTHER', 'أخرى'),
    ], default='SALES', verbose_name="تصنيف الإيراد")

    # الحساب المحاسبي الافتراضي
    default_account = models.CharField(max_length=20, blank=True, verbose_name="الحساب الافتراضي")

    # إعدادات الضرائب
    is_taxable = models.BooleanField(default=True, verbose_name="خاضع للضريبة")
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="معدل الضريبة (%)"
    )

    class Meta:
        verbose_name = "فئة إيراد"
        verbose_name_plural = "فئات الإيرادات"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.tax_rate and (self.tax_rate < 0 or self.tax_rate > 100):
            raise ValidationError('معدل الضريبة يجب أن يكون بين 0 و 100')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class RevenueItem(BaseModel):
    """بنود الإيرادات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود بند الإيراد")
    name = models.CharField(max_length=100, verbose_name="اسم بند الإيراد")
    revenue_category = models.ForeignKey(
        RevenueCategory, on_delete=models.PROTECT, verbose_name="فئة الإيراد"
    )
    description = models.TextField(blank=True, verbose_name="الوصف")

    # الحساب المحاسبي
    account_number = models.CharField(max_length=20, blank=True, verbose_name="رقم الحساب")

    # إعدادات الإيراد
    is_recurring = models.BooleanField(default=False, verbose_name="إيراد دوري")
    recurring_period = models.CharField(max_length=20, choices=[
        ('DAILY', 'يومي'),
        ('WEEKLY', 'أسبوعي'),
        ('MONTHLY', 'شهري'),
        ('QUARTERLY', 'ربع سنوي'),
        ('YEARLY', 'سنوي'),
    ], blank=True, verbose_name="فترة التكرار")

    # إعدادات الضرائب
    is_taxable = models.BooleanField(default=True, verbose_name="خاضع للضريبة")
    tax_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="معدل الضريبة (%)"
    )

    # حدود المبلغ
    min_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأدنى للمبلغ"
    )
    max_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="الحد الأقصى للمبلغ"
    )

    # إعدادات
    requires_contract = models.BooleanField(default=False, verbose_name="يتطلب عقد")
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="معدل العمولة (%)"
    )

    class Meta:
        verbose_name = "بند إيراد"
        verbose_name_plural = "بنود الإيرادات"
        ordering = ['revenue_category', 'name']

    def __str__(self):
        return f"{self.name} ({self.revenue_category.name})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.tax_rate and (self.tax_rate < 0 or self.tax_rate > 100):
            raise ValidationError('معدل الضريبة يجب أن يكون بين 0 و 100')

        if self.commission_rate and (self.commission_rate < 0 or self.commission_rate > 100):
            raise ValidationError('معدل العمولة يجب أن يكون بين 0 و 100')

        if self.min_amount and self.min_amount < 0:
            raise ValidationError('الحد الأدنى للمبلغ لا يمكن أن يكون سالباً')

        if self.max_amount and self.max_amount <= 0:
            raise ValidationError('الحد الأقصى للمبلغ يجب أن يكون أكبر من صفر')

        if self.min_amount and self.max_amount and self.min_amount > self.max_amount:
            raise ValidationError('الحد الأدنى للمبلغ لا يمكن أن يكون أكبر من الحد الأقصى')

        if self.is_recurring and not self.recurring_period:
            raise ValidationError('يجب تحديد فترة التكرار للإيراد الدوري')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """الاسم الكامل مع فئة الإيراد"""
        return f"{self.revenue_category.name} - {self.name}"

    def calculate_tax(self, amount):
        """حساب الضريبة على المبلغ"""
        if not self.is_taxable or not self.tax_rate:
            return 0
        return amount * (self.tax_rate / 100)

    def calculate_commission(self, amount):
        """حساب العمولة على المبلغ"""
        if not self.commission_rate:
            return 0
        return amount * (self.commission_rate / 100)


class FinancialAlert(BaseModel):
    """نموذج التنبيهات المالية"""

    ALERT_TYPES = [
        ('EXPENSE_LIMIT', 'تجاوز حد المصروف'),
        ('RECURRING_DUE', 'مصروف دوري مستحق'),
        ('APPROVAL_REQUIRED', 'يتطلب موافقة'),
        ('DOCUMENT_MISSING', 'مستند مفقود'),
        ('REVENUE_TARGET', 'هدف إيراد'),
        ('TAX_CALCULATION', 'حساب ضريبة'),
    ]

    PRIORITY_LEVELS = [
        ('LOW', 'منخفض'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'عالي'),
        ('URGENT', 'عاجل'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'معلق'),
        ('ACKNOWLEDGED', 'تم الاطلاع'),
        ('RESOLVED', 'تم الحل'),
        ('DISMISSED', 'تم التجاهل'),
    ]

    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name="نوع التنبيه"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="عنوان التنبيه"
    )

    message = models.TextField(
        verbose_name="رسالة التنبيه"
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='MEDIUM',
        verbose_name="مستوى الأولوية"
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="حالة التنبيه"
    )

    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='financial_alerts',
        verbose_name="المستخدم المستهدف"
    )

    expense_category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="فئة المصروف"
    )

    expense_item = models.ForeignKey(
        ExpenseItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="بند المصروف"
    )

    revenue_category = models.ForeignKey(
        RevenueCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="فئة الإيراد"
    )

    revenue_item = models.ForeignKey(
        RevenueItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="بند الإيراد"
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="المبلغ"
    )

    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الاستحقاق"
    )

    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الاطلاع"
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الحل"
    )

    def mark_acknowledged(self):
        """تحديد التنبيه كمطلع عليه"""
        from django.utils import timezone
        self.status = 'ACKNOWLEDGED'
        self.acknowledged_at = timezone.now()
        self.save()

    def mark_resolved(self):
        """تحديد التنبيه كمحلول"""
        from django.utils import timezone
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.save()

    def get_priority_color(self):
        """إرجاع لون الأولوية"""
        colors = {
            'LOW': 'success',
            'MEDIUM': 'warning',
            'HIGH': 'danger',
            'URGENT': 'dark'
        }
        return colors.get(self.priority, 'secondary')

    def get_type_icon(self):
        """إرجاع أيقونة نوع التنبيه"""
        icons = {
            'EXPENSE_LIMIT': 'fas fa-exclamation-triangle',
            'RECURRING_DUE': 'fas fa-clock',
            'APPROVAL_REQUIRED': 'fas fa-user-check',
            'DOCUMENT_MISSING': 'fas fa-file-times',
            'REVENUE_TARGET': 'fas fa-bullseye',
            'TAX_CALCULATION': 'fas fa-calculator',
        }
        return icons.get(self.alert_type, 'fas fa-bell')

    def __str__(self):
        return f"{self.title} - {self.target_user.username}"

    class Meta:
        verbose_name = "تنبيه مالي"
        verbose_name_plural = "التنبيهات المالية"
        ordering = ['-created_at', 'priority']


class ProductionStage(BaseModel):
    """مراحل الإنتاج"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود المرحلة")
    name = models.CharField(max_length=100, verbose_name="اسم المرحلة")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # ترتيب المرحلة
    sequence_number = models.IntegerField(verbose_name="رقم التسلسل")

    # نوع المرحلة
    stage_type = models.CharField(max_length=20, choices=[
        ('PREPARATION', 'تحضير'),
        ('PROCESSING', 'تشغيل'),
        ('ASSEMBLY', 'تجميع'),
        ('TESTING', 'اختبار'),
        ('PACKAGING', 'تعبئة'),
        ('QUALITY_CONTROL', 'مراقبة جودة'),
        ('FINISHING', 'تشطيب'),
        ('OTHER', 'أخرى'),
    ], default='PROCESSING', verbose_name="نوع المرحلة")

    # الموقع والمعدات
    location = models.CharField(max_length=200, blank=True, verbose_name="الموقع")
    required_equipment = models.TextField(blank=True, verbose_name="المعدات المطلوبة")

    # الوقت المطلوب
    estimated_duration_hours = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="المدة المقدرة (ساعات)"
    )
    setup_time_hours = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        verbose_name="وقت الإعداد (ساعات)"
    )

    # التكلفة
    labor_cost_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="تكلفة العمالة/ساعة"
    )
    overhead_cost_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="التكاليف الإضافية/ساعة"
    )

    # المسؤول عن المرحلة
    responsible_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="production_stages", verbose_name="المسؤول"
    )

    # إعدادات المرحلة
    requires_approval = models.BooleanField(default=False, verbose_name="تتطلب موافقة")
    requires_quality_check = models.BooleanField(default=True, verbose_name="تتطلب فحص جودة")
    is_critical = models.BooleanField(default=False, verbose_name="مرحلة حرجة")
    can_run_parallel = models.BooleanField(default=False, verbose_name="يمكن تشغيلها بالتوازي")

    # معايير الجودة
    quality_standards = models.TextField(blank=True, verbose_name="معايير الجودة")
    acceptance_criteria = models.TextField(blank=True, verbose_name="معايير القبول")

    # الحساب المحاسبي
    cost_center = models.CharField(max_length=20, blank=True, verbose_name="مركز التكلفة")

    class Meta:
        verbose_name = "مرحلة إنتاج"
        verbose_name_plural = "مراحل الإنتاج"
        ordering = ['sequence_number', 'name']

    def __str__(self):
        return f"{self.sequence_number}. {self.name}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.estimated_duration_hours and self.estimated_duration_hours <= 0:
            raise ValidationError('المدة المقدرة يجب أن تكون أكبر من صفر')

        if self.setup_time_hours and self.setup_time_hours < 0:
            raise ValidationError('وقت الإعداد لا يمكن أن يكون سالباً')

        if self.labor_cost_per_hour and self.labor_cost_per_hour < 0:
            raise ValidationError('تكلفة العمالة لا يمكن أن تكون سالبة')

        if self.overhead_cost_per_hour and self.overhead_cost_per_hour < 0:
            raise ValidationError('التكاليف الإضافية لا يمكن أن تكون سالبة')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_cost_per_hour(self):
        """إجمالي التكلفة في الساعة"""
        labor_cost = self.labor_cost_per_hour or 0
        overhead_cost = self.overhead_cost_per_hour or 0
        return labor_cost + overhead_cost

    def calculate_stage_cost(self, duration_hours=None):
        """حساب تكلفة المرحلة"""
        if duration_hours is None:
            duration_hours = self.estimated_duration_hours or 0

        setup_cost = (self.setup_time_hours or 0) * self.total_cost_per_hour
        processing_cost = duration_hours * self.total_cost_per_hour

        return setup_cost + processing_cost


class FinishedProduct(BaseModel):
    """المنتجات التامة"""
    code = models.CharField(max_length=50, unique=True, verbose_name="كود المنتج")
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    name_english = models.CharField(max_length=200, blank=True, verbose_name="الاسم بالإنجليزية")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # تصنيف المنتج
    category = models.ForeignKey(
        ItemCategory, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="فئة المنتج"
    )

    # وحدة القياس
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="وحدة القياس")

    # معلومات المنتج
    brand = models.CharField(max_length=100, blank=True, verbose_name="العلامة التجارية")
    model = models.CharField(max_length=100, blank=True, verbose_name="الموديل")
    version = models.CharField(max_length=50, blank=True, verbose_name="الإصدار")

    # الباركود والمعرفات
    barcode = models.CharField(max_length=100, blank=True, unique=True, null=True, verbose_name="الباركود")
    sku = models.CharField(max_length=100, blank=True, verbose_name="رقم المنتج")

    # المواصفات الفنية
    specifications = models.TextField(blank=True, verbose_name="المواصفات الفنية")
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        verbose_name="الوزن (كجم)"
    )
    dimensions = models.CharField(max_length=100, blank=True, verbose_name="الأبعاد")
    color = models.CharField(max_length=50, blank=True, verbose_name="اللون")
    material = models.CharField(max_length=100, blank=True, verbose_name="المادة")

    # معلومات التكلفة والسعر
    standard_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="التكلفة المعيارية"
    )
    material_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="تكلفة المواد"
    )
    labor_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="تكلفة العمالة"
    )
    overhead_cost = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="التكاليف الإضافية"
    )

    # أسعار البيع
    selling_price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="سعر البيع"
    )
    wholesale_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="سعر الجملة"
    )
    retail_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="سعر التجزئة"
    )

    # حدود المخزون
    min_stock = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="الحد الأدنى للمخزون"
    )
    max_stock = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="الحد الأقصى للمخزون"
    )
    reorder_point = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="نقطة إعادة الطلب"
    )

    # معلومات الإنتاج
    production_lead_time = models.IntegerField(
        null=True, blank=True, verbose_name="مدة الإنتاج (أيام)"
    )
    batch_size = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="حجم الدفعة"
    )

    # معلومات الجودة
    quality_grade = models.CharField(max_length=20, choices=[
        ('A', 'ممتاز'),
        ('B', 'جيد جداً'),
        ('C', 'جيد'),
        ('D', 'مقبول'),
    ], blank=True, verbose_name="درجة الجودة")

    shelf_life_days = models.IntegerField(
        null=True, blank=True, verbose_name="مدة الصلاحية (أيام)"
    )

    # شهادات ومعايير
    certifications = models.TextField(blank=True, verbose_name="الشهادات والمعايير")
    compliance_standards = models.TextField(blank=True, verbose_name="معايير الامتثال")

    # معلومات التعبئة والتغليف
    packaging_type = models.CharField(max_length=100, blank=True, verbose_name="نوع التعبئة")
    package_weight = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        verbose_name="وزن العبوة (كجم)"
    )
    package_dimensions = models.CharField(max_length=100, blank=True, verbose_name="أبعاد العبوة")
    units_per_package = models.IntegerField(null=True, blank=True, verbose_name="الوحدات في العبوة")

    # الحسابات المحاسبية
    inventory_account = models.CharField(max_length=20, blank=True, verbose_name="حساب المخزون")
    cogs_account = models.CharField(max_length=20, blank=True, verbose_name="حساب تكلفة البضاعة المباعة")
    revenue_account = models.CharField(max_length=20, blank=True, verbose_name="حساب الإيرادات")

    # إعدادات
    is_manufactured = models.BooleanField(default=True, verbose_name="منتج مصنع")
    is_sellable = models.BooleanField(default=True, verbose_name="قابل للبيع")
    is_purchasable = models.BooleanField(default=False, verbose_name="قابل للشراء")
    track_serial_numbers = models.BooleanField(default=False, verbose_name="تتبع الأرقام التسلسلية")
    track_lot_numbers = models.BooleanField(default=False, verbose_name="تتبع أرقام الدفعات")

    # صور ومرفقات
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="صورة المنتج")
    technical_drawing = models.FileField(
        upload_to='products/drawings/', blank=True, null=True,
        verbose_name="الرسم الفني"
    )

    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "منتج تام"
        verbose_name_plural = "المنتجات التامة"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        from django.core.exceptions import ValidationError

        # التحقق من التكاليف
        if self.standard_cost < 0:
            raise ValidationError('التكلفة المعيارية لا يمكن أن تكون سالبة')

        if self.material_cost < 0:
            raise ValidationError('تكلفة المواد لا يمكن أن تكون سالبة')

        if self.labor_cost < 0:
            raise ValidationError('تكلفة العمالة لا يمكن أن تكون سالبة')

        if self.overhead_cost < 0:
            raise ValidationError('التكاليف الإضافية لا يمكن أن تكون سالبة')

        # التحقق من الأسعار
        if self.selling_price < 0:
            raise ValidationError('سعر البيع لا يمكن أن يكون سالباً')

        if self.wholesale_price and self.wholesale_price < 0:
            raise ValidationError('سعر الجملة لا يمكن أن يكون سالباً')

        if self.retail_price and self.retail_price < 0:
            raise ValidationError('سعر التجزئة لا يمكن أن يكون سالباً')

        # التحقق من حدود المخزون
        if self.min_stock < 0:
            raise ValidationError('الحد الأدنى للمخزون لا يمكن أن يكون سالباً')

        if self.max_stock < 0:
            raise ValidationError('الحد الأقصى للمخزون لا يمكن أن يكون سالباً')

        if self.max_stock > 0 and self.min_stock > self.max_stock:
            raise ValidationError('الحد الأدنى للمخزون لا يمكن أن يكون أكبر من الحد الأقصى')

        # التحقق من معلومات الإنتاج
        if self.production_lead_time and self.production_lead_time < 0:
            raise ValidationError('مدة الإنتاج لا يمكن أن تكون سالبة')

        if self.batch_size and self.batch_size <= 0:
            raise ValidationError('حجم الدفعة يجب أن يكون أكبر من صفر')

        if self.shelf_life_days and self.shelf_life_days <= 0:
            raise ValidationError('مدة الصلاحية يجب أن تكون أكبر من صفر')

        if self.units_per_package and self.units_per_package <= 0:
            raise ValidationError('عدد الوحدات في العبوة يجب أن يكون أكبر من صفر')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_cost(self):
        """إجمالي التكلفة"""
        return self.material_cost + self.labor_cost + self.overhead_cost

    @property
    def profit_margin(self):
        """هامش الربح"""
        if self.selling_price > 0 and self.total_cost > 0:
            return ((self.selling_price - self.total_cost) / self.selling_price) * 100
        return 0

    @property
    def markup_percentage(self):
        """نسبة الزيادة على التكلفة"""
        if self.total_cost > 0:
            return ((self.selling_price - self.total_cost) / self.total_cost) * 100
        return 0

    def calculate_cost_breakdown(self):
        """تفصيل التكلفة"""
        total = self.total_cost
        if total == 0:
            return {
                'material_percentage': 0,
                'labor_percentage': 0,
                'overhead_percentage': 0
            }

        return {
            'material_percentage': (self.material_cost / total) * 100,
            'labor_percentage': (self.labor_cost / total) * 100,
            'overhead_percentage': (self.overhead_cost / total) * 100
        }


class ProfitCenter(BaseModel):
    """مراكز الربحية"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود مركز الربحية")
    name = models.CharField(max_length=100, verbose_name="اسم مركز الربحية")
    name_english = models.CharField(max_length=100, blank=True, verbose_name="الاسم بالإنجليزية")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # التصنيف والهيكل
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name="مركز الربحية الأب"
    )
    level = models.IntegerField(default=1, verbose_name="المستوى")

    # المسؤوليات
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="managed_profit_centers", verbose_name="المدير المسؤول"
    )

    # الموقع والمعلومات
    location = models.CharField(max_length=200, blank=True, verbose_name="الموقع")
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")

    # الأهداف المالية
    target_revenue = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="هدف الإيرادات السنوي"
    )
    target_profit = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        verbose_name="هدف الربح السنوي"
    )
    target_profit_margin = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="هدف هامش الربح (%)"
    )

    # فترة التقييم
    evaluation_period = models.CharField(max_length=20, choices=[
        ('MONTHLY', 'شهري'),
        ('QUARTERLY', 'ربع سنوي'),
        ('SEMI_ANNUAL', 'نصف سنوي'),
        ('ANNUAL', 'سنوي'),
    ], default='QUARTERLY', verbose_name="فترة التقييم")

    # الحسابات المحاسبية
    revenue_account = models.CharField(max_length=20, blank=True, verbose_name="حساب الإيرادات")
    expense_account = models.CharField(max_length=20, blank=True, verbose_name="حساب المصروفات")
    asset_account = models.CharField(max_length=20, blank=True, verbose_name="حساب الأصول")

    # إعدادات التكلفة
    allocate_overhead = models.BooleanField(default=True, verbose_name="توزيع التكاليف الإضافية")
    overhead_allocation_method = models.CharField(max_length=20, choices=[
        ('REVENUE_BASED', 'على أساس الإيرادات'),
        ('EMPLOYEE_BASED', 'على أساس عدد الموظفين'),
        ('ASSET_BASED', 'على أساس الأصول'),
        ('EQUAL', 'توزيع متساوي'),
        ('CUSTOM', 'طريقة مخصصة'),
    ], default='REVENUE_BASED', verbose_name="طريقة توزيع التكاليف")

    overhead_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="نسبة التكاليف الإضافية (%)"
    )

    # إعدادات التقارير
    include_in_reports = models.BooleanField(default=True, verbose_name="تضمين في التقارير")
    consolidate_children = models.BooleanField(default=True, verbose_name="دمج البيانات من المراكز الفرعية")

    # تواريخ مهمة
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ النهاية")

    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "مركز ربحية"
        verbose_name_plural = "مراكز الربحية"
        ordering = ['level', 'code', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        from django.core.exceptions import ValidationError

        # التحقق من التواريخ
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')

        # التحقق من الأهداف المالية
        if self.target_revenue and self.target_revenue < 0:
            raise ValidationError('هدف الإيرادات لا يمكن أن يكون سالباً')

        if self.target_profit and self.target_profit < 0:
            raise ValidationError('هدف الربح لا يمكن أن يكون سالباً')

        # التحقق من المستوى
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1

        # التحقق من عدم وجود دورة في الهيكل
        if self.parent:
            current = self.parent
            while current:
                if current == self:
                    raise ValidationError('لا يمكن أن يكون مركز الربحية أباً لنفسه')
                current = current.parent

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_active_period(self):
        """هل مركز الربحية نشط في الفترة الحالية"""
        from django.utils import timezone
        today = timezone.now().date()

        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today

    @property
    def full_code(self):
        """الكود الكامل مع الهيكل"""
        if self.parent:
            return f"{self.parent.full_code}.{self.code}"
        return self.code

    @property
    def full_name(self):
        """الاسم الكامل مع الهيكل"""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name

    def get_children_count(self):
        """عدد مراكز الربحية الفرعية"""
        return self.children.filter(is_active=True).count()

    def get_all_children(self):
        """جميع مراكز الربحية الفرعية (متداخلة)"""
        children = []
        for child in self.children.filter(is_active=True):
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def calculate_target_achievement(self, actual_revenue=None, actual_profit=None):
        """حساب نسبة تحقيق الأهداف"""
        achievement = {}

        if self.target_revenue and actual_revenue is not None:
            achievement['revenue_achievement'] = (actual_revenue / self.target_revenue) * 100

        if self.target_profit and actual_profit is not None:
            achievement['profit_achievement'] = (actual_profit / self.target_profit) * 100

        if actual_revenue and actual_profit:
            actual_margin = (actual_profit / actual_revenue) * 100
            if self.target_profit_margin:
                achievement['margin_achievement'] = (actual_margin / self.target_profit_margin) * 100
            achievement['actual_margin'] = actual_margin

        return achievement


class Printer(BaseModel):
    """الطابعات"""
    code = models.CharField(max_length=20, unique=True, verbose_name="كود الطابعة")
    name = models.CharField(max_length=100, verbose_name="اسم الطابعة")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # معلومات الطابعة
    brand = models.CharField(max_length=50, blank=True, verbose_name="العلامة التجارية")
    model = models.CharField(max_length=50, blank=True, verbose_name="الموديل")
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="الرقم التسلسلي")

    # نوع الطابعة
    printer_type = models.CharField(max_length=20, choices=[
        ('THERMAL', 'حرارية'),
        ('INKJET', 'نفث الحبر'),
        ('LASER', 'ليزر'),
        ('DOT_MATRIX', 'نقطية'),
        ('LABEL', 'ملصقات'),
        ('RECEIPT', 'فواتير'),
        ('BARCODE', 'باركود'),
        ('PHOTO', 'صور'),
        ('OTHER', 'أخرى'),
    ], default='THERMAL', verbose_name="نوع الطابعة")

    # الاتصال
    connection_type = models.CharField(max_length=20, choices=[
        ('USB', 'USB'),
        ('NETWORK', 'شبكة'),
        ('BLUETOOTH', 'بلوتوث'),
        ('WIFI', 'واي فاي'),
        ('SERIAL', 'تسلسلي'),
        ('PARALLEL', 'متوازي'),
    ], default='USB', verbose_name="نوع الاتصال")

    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="عنوان IP"
    )
    port = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name="رقم المنفذ"
    )

    # إعدادات الطباعة
    paper_size = models.CharField(max_length=20, choices=[
        ('A4', 'A4'),
        ('A5', 'A5'),
        ('LETTER', 'Letter'),
        ('RECEIPT_80MM', 'فاتورة 80 مم'),
        ('RECEIPT_58MM', 'فاتورة 58 مم'),
        ('LABEL_4X6', 'ملصق 4×6'),
        ('CUSTOM', 'مخصص'),
    ], default='A4', verbose_name="حجم الورق")

    paper_width = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="عرض الورق (مم)"
    )
    paper_height = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        verbose_name="طول الورق (مم)"
    )

    # إعدادات متقدمة
    dpi = models.IntegerField(
        null=True, blank=True, verbose_name="دقة الطباعة (DPI)"
    )
    print_speed = models.CharField(max_length=20, choices=[
        ('SLOW', 'بطيء'),
        ('NORMAL', 'عادي'),
        ('FAST', 'سريع'),
    ], default='NORMAL', verbose_name="سرعة الطباعة")

    color_support = models.BooleanField(default=False, verbose_name="دعم الألوان")
    duplex_support = models.BooleanField(default=False, verbose_name="دعم الطباعة على الوجهين")

    # الموقع والاستخدام
    location = models.CharField(max_length=200, blank=True, verbose_name="الموقع")
    department = models.CharField(max_length=100, blank=True, verbose_name="القسم")

    # المسؤول
    responsible_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="managed_printers", verbose_name="المسؤول"
    )

    # الاستخدام
    usage_type = models.CharField(max_length=20, choices=[
        ('INVOICES', 'الفواتير'),
        ('REPORTS', 'التقارير'),
        ('LABELS', 'الملصقات'),
        ('RECEIPTS', 'الإيصالات'),
        ('BARCODES', 'الباركود'),
        ('DOCUMENTS', 'المستندات'),
        ('GENERAL', 'عام'),
    ], default='GENERAL', verbose_name="نوع الاستخدام")

    # إعدادات النظام
    is_default = models.BooleanField(default=False, verbose_name="الطابعة الافتراضية")
    is_shared = models.BooleanField(default=False, verbose_name="طابعة مشتركة")
    auto_cut = models.BooleanField(default=False, verbose_name="قطع تلقائي للورق")
    cash_drawer = models.BooleanField(default=False, verbose_name="فتح درج النقد")

    # معلومات الصيانة
    purchase_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الشراء")
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name="انتهاء الضمان")
    last_maintenance = models.DateField(null=True, blank=True, verbose_name="آخر صيانة")
    next_maintenance = models.DateField(null=True, blank=True, verbose_name="الصيانة القادمة")

    # إحصائيات
    total_pages_printed = models.IntegerField(default=0, verbose_name="إجمالي الصفحات المطبوعة")
    pages_this_month = models.IntegerField(default=0, verbose_name="صفحات هذا الشهر")

    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "طابعة"
        verbose_name_plural = "الطابعات"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        from django.core.exceptions import ValidationError

        # التحقق من عنوان IP والمنفذ للطابعات الشبكية
        if self.connection_type in ['NETWORK', 'WIFI']:
            if not self.ip_address:
                raise ValidationError('عنوان IP مطلوب للطابعات الشبكية')

        # التحقق من أبعاد الورق المخصص
        if self.paper_size == 'CUSTOM':
            if not self.paper_width or not self.paper_height:
                raise ValidationError('أبعاد الورق مطلوبة للحجم المخصص')

        # التحقق من التواريخ
        if self.warranty_expiry and self.purchase_date and self.warranty_expiry <= self.purchase_date:
            raise ValidationError('تاريخ انتهاء الضمان يجب أن يكون بعد تاريخ الشراء')

        if self.next_maintenance and self.last_maintenance and self.next_maintenance <= self.last_maintenance:
            raise ValidationError('تاريخ الصيانة القادمة يجب أن يكون بعد آخر صيانة')

    def save(self, *args, **kwargs):
        self.clean()

        # إذا كانت هذه الطابعة افتراضية، قم بإلغاء الافتراضية من الطابعات الأخرى
        if self.is_default:
            Printer.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)

    @property
    def connection_string(self):
        """سلسلة الاتصال"""
        if self.connection_type in ['NETWORK', 'WIFI'] and self.ip_address:
            if self.port:
                return f"{self.ip_address}:{self.port}"
            return self.ip_address
        return self.connection_type

    @property
    def is_network_printer(self):
        """هل الطابعة شبكية"""
        return self.connection_type in ['NETWORK', 'WIFI']

    @property
    def warranty_status(self):
        """حالة الضمان"""
        if not self.warranty_expiry:
            return 'غير محدد'

        from django.utils import timezone
        today = timezone.now().date()

        if self.warranty_expiry > today:
            days_left = (self.warranty_expiry - today).days
            if days_left <= 30:
                return f'ينتهي خلال {days_left} يوم'
            return 'ساري'
        return 'منتهي'

    @property
    def maintenance_status(self):
        """حالة الصيانة"""
        if not self.next_maintenance:
            return 'غير محدد'

        from django.utils import timezone
        today = timezone.now().date()

        if self.next_maintenance > today:
            days_left = (self.next_maintenance - today).days
            if days_left <= 7:
                return f'مطلوبة خلال {days_left} يوم'
            return 'مجدولة'
        return 'متأخرة'

    def get_paper_dimensions(self):
        """الحصول على أبعاد الورق"""
        if self.paper_size == 'CUSTOM':
            return f"{self.paper_width}×{self.paper_height} مم"
        return self.get_paper_size_display()

    def reset_monthly_counter(self):
        """إعادة تعيين عداد الشهر"""
        self.pages_this_month = 0
        self.save()






def company_logo_upload_path(instance, filename):
    """مسار رفع شعار الشركة"""
    from django.utils import timezone

    # الحصول على امتداد الملف
    ext = filename.split('.')[-1].lower()

    # إنشاء اسم ملف جديد مع الوقت الحالي
    new_filename = f"company_logo_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"

    return os.path.join('company', 'logos', new_filename)


class CompanySettings(BaseModel):
    """إعدادات الشركة والتطبيق"""

    # معلومات الشركة الأساسية
    company_name = models.CharField(max_length=200, verbose_name="اسم الشركة")
    company_name_english = models.CharField(max_length=200, blank=True, verbose_name="اسم الشركة بالإنجليزية")

    # الشعار
    logo = models.ImageField(
        upload_to=company_logo_upload_path,
        blank=True,
        null=True,
        verbose_name="شعار الشركة",
        help_text="يفضل أن يكون الشعار بصيغة PNG أو JPG وبحجم 200x200 بكسل"
    )

    # معلومات الاتصال
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    mobile = models.CharField(max_length=20, blank=True, verbose_name="الجوال")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    website = models.URLField(blank=True, verbose_name="الموقع الإلكتروني")

    # العنوان
    address = models.TextField(blank=True, verbose_name="العنوان")
    city = models.CharField(max_length=100, blank=True, verbose_name="المدينة")
    state = models.CharField(max_length=100, blank=True, verbose_name="المحافظة")
    country = models.CharField(max_length=100, default='مصر', verbose_name="الدولة")
    postal_code = models.CharField(max_length=10, blank=True, verbose_name="الرمز البريدي")

    # معلومات قانونية
    tax_number = models.CharField(max_length=20, blank=True, verbose_name="الرقم الضريبي")
    commercial_register = models.CharField(max_length=20, blank=True, verbose_name="السجل التجاري")

    # العملة الافتراضية
    default_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="العملة الافتراضية"
    )

    # إعدادات التطبيق
    app_name = models.CharField(max_length=100, default="نظام الحسابات", verbose_name="اسم التطبيق")
    app_version = models.CharField(max_length=20, default="1.0.0", verbose_name="إصدار التطبيق")

    # إعدادات العرض
    items_per_page = models.IntegerField(default=25, verbose_name="عدد العناصر في الصفحة")
    date_format = models.CharField(
        max_length=20,
        default='%d/%m/%Y',
        choices=[
            ('%d/%m/%Y', 'DD/MM/YYYY'),
            ('%m/%d/%Y', 'MM/DD/YYYY'),
            ('%Y-%m-%d', 'YYYY-MM-DD'),
        ],
        verbose_name="تنسيق التاريخ"
    )

    # إعدادات الأمان
    session_timeout_minutes = models.IntegerField(default=60, verbose_name="انتهاء الجلسة (دقيقة)")
    password_min_length = models.IntegerField(default=8, verbose_name="الحد الأدنى لطول كلمة المرور")

    # إعدادات النسخ الاحتياطي
    auto_backup_enabled = models.BooleanField(default=False, verbose_name="تفعيل النسخ الاحتياطي التلقائي")
    backup_frequency_days = models.IntegerField(default=7, verbose_name="تكرار النسخ الاحتياطي (أيام)")

    # إعدادات الإشعارات
    email_notifications_enabled = models.BooleanField(default=True, verbose_name="تفعيل إشعارات البريد الإلكتروني")
    sms_notifications_enabled = models.BooleanField(default=False, verbose_name="تفعيل إشعارات الرسائل النصية")

    # إعدادات التقارير
    default_report_format = models.CharField(
        max_length=10,
        default='PDF',
        choices=[
            ('PDF', 'PDF'),
            ('EXCEL', 'Excel'),
            ('CSV', 'CSV'),
        ],
        verbose_name="تنسيق التقارير الافتراضي"
    )

    # إعدادات الطباعة
    print_logo_on_reports = models.BooleanField(default=True, verbose_name="طباعة الشعار في التقارير")
    print_company_info = models.BooleanField(default=True, verbose_name="طباعة معلومات الشركة")

    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "إعدادات الشركة"
        verbose_name_plural = "إعدادات الشركة"

    def __str__(self):
        return f"إعدادات {self.company_name}"

    def save(self, *args, **kwargs):
        # التأكد من وجود إعدادات واحدة فقط
        if not self.pk and CompanySettings.objects.exists():
            raise ValidationError('يمكن وجود إعدادات شركة واحدة فقط')

        # حذف الشعار القديم عند رفع شعار جديد
        if self.pk:
            try:
                old_instance = CompanySettings.objects.get(pk=self.pk)
                if old_instance.logo and self.logo and old_instance.logo != self.logo:
                    if os.path.isfile(old_instance.logo.path):
                        os.remove(old_instance.logo.path)
            except CompanySettings.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # حذف ملف الشعار عند حذف الإعدادات
        if self.logo:
            if os.path.isfile(self.logo.path):
                os.remove(self.logo.path)
        super().delete(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """الحصول على إعدادات الشركة (إنشاء إعدادات افتراضية إذا لم توجد)"""
        settings, created = cls.objects.get_or_create(
            defaults={
                'company_name': 'شركة المحاسبة',
                'app_name': 'نظام الحسابات',
                'app_version': '1.0.0',
            }
        )
        return settings

    @property
    def logo_url(self):
        """رابط الشعار"""
        if self.logo:
            return self.logo.url
        return None

    @property
    def full_address(self):
        """العنوان الكامل"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.city:
            address_parts.append(self.city)
        if self.state:
            address_parts.append(self.state)
        if self.country:
            address_parts.append(self.country)
        return ', '.join(address_parts)

    def clean(self):
        # التحقق من صحة البريد الإلكتروني
        if self.email:
            from django.core.validators import validate_email
            try:
                validate_email(self.email)
            except:
                raise ValidationError('البريد الإلكتروني غير صحيح')

        # التحقق من إعدادات الجلسة
        if self.session_timeout_minutes <= 0:
            raise ValidationError('مدة انتهاء الجلسة يجب أن تكون أكبر من صفر')

        # التحقق من طول كلمة المرور
        if self.password_min_length < 4:
            raise ValidationError('الحد الأدنى لطول كلمة المرور يجب أن يكون 4 أحرف على الأقل')

        # التحقق من تكرار النسخ الاحتياطي
        if self.backup_frequency_days <= 0:
            raise ValidationError('تكرار النسخ الاحتياطي يجب أن يكون أكبر من صفر')

        # التحقق من عدد العناصر في الصفحة
        if self.items_per_page <= 0:
            raise ValidationError('عدد العناصر في الصفحة يجب أن يكون أكبر من صفر')
