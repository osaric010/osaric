from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from definitions.models import Person, Item, Warehouse, Currency
from decimal import Decimal
from django.utils import timezone


class Account(models.Model):
    """الحسابات المحاسبية"""
    ACCOUNT_TYPES = [
        ('ASSET', 'أصول'),
        ('LIABILITY', 'خصوم'),
        ('EQUITY', 'حقوق ملكية'),
        ('REVENUE', 'إيرادات'),
        ('EXPENSE', 'مصروفات'),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name="كود الحساب")
    name = models.CharField(max_length=100, verbose_name="اسم الحساب")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name="نوع الحساب")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="الحساب الأب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "حساب محاسبي"
        verbose_name_plural = "الحسابات المحاسبية"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class BalanceTransfer(models.Model):
    """تحويل رصيد بين الأشخاص"""
    transfer_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التحويل")
    transfer_date = models.DateField(verbose_name="تاريخ التحويل")
    from_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='transfers_from', verbose_name="من شخص")
    to_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='transfers_to', verbose_name="إلى شخص")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "تحويل رصيد"
        verbose_name_plural = "تحويلات الأرصدة"
        ordering = ['-transfer_date', '-created_at']

    def __str__(self):
        return f"{self.transfer_number} - {self.from_person.name} إلى {self.to_person.name}"


class AccountMerge(models.Model):
    """دمج الحسابات الفرعية للأشخاص"""
    merge_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الدمج")
    merge_date = models.DateField(verbose_name="تاريخ الدمج")
    source_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='merges_from', verbose_name="الشخص المصدر")
    target_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='merges_to', verbose_name="الشخص الهدف")
    merged_balance = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="الرصيد المدمج")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "دمج حسابات"
        verbose_name_plural = "دمج الحسابات"
        ordering = ['-merge_date', '-created_at']

    def __str__(self):
        return f"{self.merge_number} - دمج {self.source_person.name} في {self.target_person.name}"


class JournalEntry(models.Model):
    """القيود المحاسبية"""
    entry_number = models.CharField(max_length=50, unique=True, verbose_name="رقم القيد")
    entry_date = models.DateField(verbose_name="تاريخ القيد")
    description = models.TextField(verbose_name="الوصف")
    total_debit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="إجمالي المدين")
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="إجمالي الدائن")
    is_balanced = models.BooleanField(default=False, verbose_name="متوازن")
    is_posted = models.BooleanField(default=False, verbose_name="مرحل")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "قيد محاسبي"
        verbose_name_plural = "القيود المحاسبية"
        ordering = ['-entry_date', '-created_at']

    def __str__(self):
        return f"{self.entry_number} - {self.description[:50]}"

    def save(self, *args, **kwargs):
        # حساب الإجماليات والتوازن
        if self.pk:
            self.total_debit = self.journal_entry_lines.aggregate(
                total=models.Sum('debit_amount'))['total'] or 0
            self.total_credit = self.journal_entry_lines.aggregate(
                total=models.Sum('credit_amount'))['total'] or 0
            self.is_balanced = self.total_debit == self.total_credit
        super().save(*args, **kwargs)


class JournalEntryLine(models.Model):
    """تفاصيل القيود المحاسبية"""
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='journal_entry_lines', verbose_name="القيد المحاسبي")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="الحساب")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True, verbose_name="الشخص")
    description = models.CharField(max_length=255, verbose_name="الوصف")
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="مدين")
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="دائن")
    line_order = models.PositiveIntegerField(default=1, verbose_name="ترتيب السطر")

    class Meta:
        verbose_name = "سطر قيد محاسبي"
        verbose_name_plural = "أسطر القيود المحاسبية"
        ordering = ['journal_entry', 'line_order']

    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.name}"


class OpeningBalance(models.Model):
    """القيد الافتتاحي"""
    BALANCE_TYPES = [
        ('INVENTORY', 'جرد بضاعة أول المدة'),
        ('PERSONS', 'رصيد الأشخاص والجهات'),
        ('BANK', 'رصيد البنك'),
        ('TREASURY', 'رصيد الخزينة'),
        ('RECEIVABLE_PAPERS', 'أوراق قبض'),
        ('INCOMING_CUSTODY', 'إصالات أمانة واردة'),
        ('PAYABLE_PAPERS', 'أوراق دفع'),
        ('OUTGOING_CUSTODY', 'إيصالات أمانة صادرة'),
        ('FIXED_ASSETS', 'الأصول الثابتة'),
        ('RETAINED_EARNINGS', 'أرباح مرحلة'),
    ]

    PERSON_TYPES = [
        ('CUSTOMERS', 'عملاء'),
        ('EMPLOYEE_ADVANCES', 'سلف عاملين'),
        ('MISC_DEBTORS', 'مدينون متنوعون'),
        ('SUPPLIERS', 'موردون'),
        ('MISC_CREDITORS', 'دائنون متنوعون'),
        ('PARTNERS', 'شركاء'),
        ('PARTNER_CURRENT', 'جاري الشركاء'),
    ]

    balance_number = models.CharField(max_length=50, unique=True, verbose_name="رقم القيد الافتتاحي")
    balance_date = models.DateField(verbose_name="تاريخ القيد الافتتاحي")
    balance_type = models.CharField(max_length=20, choices=BALANCE_TYPES, verbose_name="نوع الرصيد")
    person_type = models.CharField(max_length=20, choices=PERSON_TYPES, blank=True, null=True, verbose_name="نوع الشخص")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True, verbose_name="الحساب")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True, verbose_name="الشخص")
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="مدين")
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="دائن")
    description = models.TextField(verbose_name="الوصف")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "قيد افتتاحي"
        verbose_name_plural = "القيود الافتتاحية"
        ordering = ['-balance_date', '-created_at']

    def __str__(self):
        return f"{self.balance_number} - {self.get_balance_type_display()}"


class ProfitCenter(models.Model):
    """مراكز الربحية"""
    center_code = models.CharField(max_length=20, unique=True, verbose_name="كود المركز")
    center_name = models.CharField(max_length=100, verbose_name="اسم المركز")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "مركز ربحية"
        verbose_name_plural = "مراكز الربحية"
        ordering = ['center_code']

    def __str__(self):
        return f"{self.center_code} - {self.center_name}"


class ProfitDistribution(models.Model):
    """توزيع الأرباح"""
    distribution_number = models.CharField(max_length=50, unique=True, verbose_name="رقم التوزيع")
    distribution_date = models.DateField(verbose_name="تاريخ التوزيع")
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="إجمالي الربح")
    description = models.TextField(verbose_name="الوصف")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "توزيع أرباح"
        verbose_name_plural = "توزيعات الأرباح"
        ordering = ['-distribution_date', '-created_at']

    def __str__(self):
        return f"{self.distribution_number} - {self.total_profit}"


class ProfitDistributionLine(models.Model):
    """تفاصيل توزيع الأرباح"""
    distribution = models.ForeignKey(ProfitDistribution, on_delete=models.CASCADE, related_name='distribution_lines', verbose_name="توزيع الأرباح")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="الشخص/الشريك")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="النسبة %")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="المبلغ")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="الوصف")

    class Meta:
        verbose_name = "سطر توزيع أرباح"
        verbose_name_plural = "أسطر توزيع الأرباح"
        ordering = ['distribution', 'person']

    def __str__(self):
        return f"{self.distribution.distribution_number} - {self.person.name}"


class AccountingPeriod(models.Model):
    """فترات الحسابات"""
    period_name = models.CharField(max_length=100, verbose_name="اسم الفترة")
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    is_current = models.BooleanField(default=False, verbose_name="الفترة الحالية")
    is_closed = models.BooleanField(default=False, verbose_name="مغلقة")
    closed_date = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ الإغلاق")
    closed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='closed_periods', verbose_name="أغلق بواسطة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="أنشئ بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "فترة حسابات"
        verbose_name_plural = "فترات الحسابات"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.period_name} ({self.start_date} - {self.end_date})"

    def save(self, *args, **kwargs):
        if self.is_current:
            # إلغاء تحديد الفترة الحالية للفترات الأخرى
            AccountingPeriod.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class BaseModel(models.Model):
    """النموذج الأساسي"""
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="%(class)s_created", verbose_name="أنشئ بواسطة")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="%(class)s_updated", verbose_name="عدل بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        abstract = True


class OpeningInventory(BaseModel):
    """جرد بضاعة أول المدة"""
    inventory_number = models.CharField(max_length=50, unique=True, verbose_name="رقم جرد أول المدة")
    date = models.DateField(verbose_name="تاريخ أول المدة")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="المخزن")
    fiscal_year = models.CharField(max_length=10, verbose_name="السنة المالية")
    period_name = models.CharField(max_length=100, verbose_name="اسم الفترة")

    # معلومات الحالة
    status = models.CharField(max_length=20, choices=[
        ('DRAFT', 'مسودة'),
        ('APPROVED', 'معتمد'),
        ('POSTED', 'مرحل'),
        ('CANCELLED', 'ملغي'),
    ], default='DRAFT', verbose_name="الحالة")

    # إحصائيات
    total_items = models.IntegerField(default=0, verbose_name="عدد الأصناف")
    total_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                        verbose_name="إجمالي الكميات")
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي القيمة")

    # معلومات الاعتماد والترحيل
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="approved_opening_inventories", verbose_name="معتمد من")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاعتماد")
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="posted_opening_inventories", verbose_name="رحل بواسطة")
    posted_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الترحيل")

    # العملة
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=True, blank=True,
                                verbose_name="العملة")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000,
                                       verbose_name="سعر الصرف")

    class Meta:
        verbose_name = "جرد بضاعة أول المدة"
        verbose_name_plural = "جرد بضاعة أول المدة"
        ordering = ['-date', '-id']
        unique_together = ['warehouse', 'fiscal_year']

    def clean(self):
        """التحقق من صحة البيانات"""
        super().clean()

        # التحقق من عدم وجود جرد أول مدة آخر لنفس المخزن والسنة المالية
        if self.warehouse and self.fiscal_year:
            existing = OpeningInventory.objects.filter(
                warehouse=self.warehouse,
                fiscal_year=self.fiscal_year,
                status__in=['APPROVED', 'POSTED']
            ).exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError(
                    f'يوجد بالفعل جرد أول مدة معتمد للمخزن {self.warehouse.name} '
                    f'للسنة المالية {self.fiscal_year}'
                )

    def save(self, *args, **kwargs):
        # تعيين العملة الافتراضية إذا لم تكن محددة
        if not self.currency_id:
            try:
                default_currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
                if default_currency:
                    self.currency = default_currency
                    self.exchange_rate = default_currency.exchange_rate
            except:
                pass

        # حساب الإحصائيات
        if self.pk:
            items = self.items.all()
            self.total_items = items.count()
            self.total_quantity = sum(item.opening_quantity for item in items)
            self.total_value = sum(item.total_value for item in items)

        super().save(*args, **kwargs)

    @property
    def can_be_edited(self):
        """هل يمكن تعديل الجرد"""
        return self.status in ['DRAFT']

    @property
    def can_be_approved(self):
        """هل يمكن اعتماد الجرد"""
        return self.status == 'DRAFT' and self.total_items > 0

    @property
    def can_be_posted(self):
        """هل يمكن ترحيل الجرد"""
        return self.status == 'APPROVED'

    @property
    def can_be_cancelled(self):
        """هل يمكن إلغاء الجرد"""
        return self.status in ['DRAFT', 'APPROVED']

    @property
    def is_posted(self):
        """هل تم ترحيل الجرد"""
        return self.status == 'POSTED'

    def __str__(self):
        return f"{self.inventory_number} - {self.warehouse.name} ({self.fiscal_year})"


class OpeningInventoryItem(BaseModel):
    """أصناف جرد بضاعة أول المدة"""
    opening_inventory = models.ForeignKey(OpeningInventory, on_delete=models.CASCADE,
                                         related_name="items", verbose_name="جرد أول المدة")
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="الصنف")

    # الكميات والتكاليف
    opening_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0,
                                          verbose_name="كمية أول المدة")
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                   verbose_name="تكلفة الوحدة")
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="إجمالي القيمة")

    # معلومات إضافية للصنف
    expiry_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")
    batch_number = models.CharField(max_length=50, blank=True, verbose_name="رقم الدفعة")
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="الرقم التسلسلي")
    location = models.CharField(max_length=100, blank=True, verbose_name="الموقع في المخزن")

    # معلومات الجودة والحالة
    condition = models.CharField(max_length=20, choices=[
        ('NEW', 'جديد'),
        ('GOOD', 'جيد'),
        ('FAIR', 'مقبول'),
        ('POOR', 'ضعيف'),
        ('DAMAGED', 'تالف'),
    ], default='GOOD', verbose_name="الحالة")

    quality_grade = models.CharField(max_length=20, choices=[
        ('A', 'ممتاز'),
        ('B', 'جيد جداً'),
        ('C', 'جيد'),
        ('D', 'مقبول'),
    ], blank=True, verbose_name="درجة الجودة")

    # ملاحظات
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    # معلومات التسجيل
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="سجل بواسطة")
    recorded_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    class Meta:
        verbose_name = "صنف جرد أول المدة"
        verbose_name_plural = "أصناف جرد أول المدة"
        unique_together = ['opening_inventory', 'item', 'batch_number']
        ordering = ['item__name']

    def clean(self):
        """التحقق من صحة البيانات"""
        super().clean()

        # التحقق من أن الكمية موجبة
        if self.opening_quantity < 0:
            raise ValidationError('كمية أول المدة يجب أن تكون موجبة')

        # التحقق من أن تكلفة الوحدة موجبة
        if self.unit_cost < 0:
            raise ValidationError('تكلفة الوحدة يجب أن تكون موجبة')

        # التحقق من تاريخ الانتهاء
        if self.expiry_date:
            from datetime import date
            if self.expiry_date <= date.today():
                raise ValidationError('تاريخ الانتهاء يجب أن يكون في المستقبل')

    def save(self, *args, **kwargs):
        # حساب إجمالي القيمة
        self.total_value = self.opening_quantity * self.unit_cost

        # تعيين تكلفة الوحدة من الصنف إذا لم تكن محددة
        if not self.unit_cost and self.item:
            self.unit_cost = self.item.cost_price or Decimal('0.00')
            self.total_value = self.opening_quantity * self.unit_cost

        super().save(*args, **kwargs)

        # تحديث إحصائيات جرد أول المدة
        if self.opening_inventory:
            self.opening_inventory.save()

    def delete(self, *args, **kwargs):
        opening_inventory = self.opening_inventory
        super().delete(*args, **kwargs)

        # تحديث إحصائيات جرد أول المدة بعد الحذف
        if opening_inventory:
            opening_inventory.save()

    @property
    def is_expired(self):
        """هل الصنف منتهي الصلاحية"""
        if self.expiry_date:
            from datetime import date
            return date.today() > self.expiry_date
        return False

    @property
    def days_until_expiry(self):
        """عدد الأيام حتى انتهاء الصلاحية"""
        if self.expiry_date:
            from datetime import date
            delta = self.expiry_date - date.today()
            return delta.days
        return None

    @property
    def is_near_expiry(self):
        """هل الصنف قريب من انتهاء الصلاحية (أقل من 30 يوم)"""
        days = self.days_until_expiry
        return days is not None and 0 < days <= 30

    def __str__(self):
        return f"{self.item.name} - {self.opening_quantity} ({self.opening_inventory.inventory_number})"
