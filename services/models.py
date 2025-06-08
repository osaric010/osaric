from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class DeletedRecord(models.Model):
    """سجل البيانات المحذوفة"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="نوع البيانات")
    object_id = models.PositiveIntegerField(verbose_name="معرف الكائن")
    content_object = GenericForeignKey('content_type', 'object_id')

    # بيانات الكائن المحذوف
    object_data = models.JSONField(verbose_name="بيانات الكائن")
    object_repr = models.CharField(max_length=200, verbose_name="تمثيل الكائن")

    # معلومات الحذف
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="حُذف بواسطة")
    deleted_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الحذف")
    deletion_reason = models.TextField(blank=True, verbose_name="سبب الحذف")

    # حالة السجل
    is_restored = models.BooleanField(default=False, verbose_name="تم الاسترداد")
    restored_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="restored_records", verbose_name="استُرد بواسطة")
    restored_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الاسترداد")

    class Meta:
        verbose_name = "سجل محذوف"
        verbose_name_plural = "السجلات المحذوفة"
        ordering = ['-deleted_at']

    def __str__(self):
        return f"{self.content_type.name} - {self.object_repr}"


class EditHistory(models.Model):
    """تاريخ التعديلات"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="نوع البيانات")
    object_id = models.PositiveIntegerField(verbose_name="معرف الكائن")
    content_object = GenericForeignKey('content_type', 'object_id')

    # بيانات التعديل
    field_name = models.CharField(max_length=100, verbose_name="اسم الحقل")
    old_value = models.TextField(blank=True, verbose_name="القيمة القديمة")
    new_value = models.TextField(blank=True, verbose_name="القيمة الجديدة")

    # معلومات التعديل
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="عُدل بواسطة")
    edited_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التعديل")
    edit_reason = models.TextField(blank=True, verbose_name="سبب التعديل")

    # معلومات إضافية
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="معلومات المتصفح")

    class Meta:
        verbose_name = "تاريخ تعديل"
        verbose_name_plural = "تاريخ التعديلات"
        ordering = ['-edited_at']

    def __str__(self):
        return f"{self.content_type.name} - {self.field_name} - {self.edited_at}"


class SystemBackup(models.Model):
    """النسخ الاحتياطية"""
    BACKUP_TYPES = [
        ('FULL', 'نسخة كاملة'),
        ('PARTIAL', 'نسخة جزئية'),
        ('INCREMENTAL', 'نسخة تزايدية'),
    ]

    backup_name = models.CharField(max_length=200, verbose_name="اسم النسخة")
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPES, default='FULL', verbose_name="نوع النسخة")
    file_path = models.CharField(max_length=500, verbose_name="مسار الملف")
    file_size = models.BigIntegerField(verbose_name="حجم الملف (بايت)")

    # معلومات النسخة
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئت بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    description = models.TextField(blank=True, verbose_name="الوصف")

    # إعدادات النسخة
    include_media = models.BooleanField(default=True, verbose_name="تضمين ملفات الوسائط")
    include_logs = models.BooleanField(default=False, verbose_name="تضمين ملفات السجلات")
    compress_backup = models.BooleanField(default=True, verbose_name="ضغط النسخة")

    # حالة النسخة
    is_valid = models.BooleanField(default=True, verbose_name="نسخة صالحة")
    checksum = models.CharField(max_length=64, blank=True, verbose_name="المجموع التحققي")

    class Meta:
        verbose_name = "نسخة احتياطية"
        verbose_name_plural = "النسخ الاحتياطية"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.backup_name} - {self.created_at}"

    @property
    def file_size_mb(self):
        """حجم الملف بالميجابايت"""
        return round(self.file_size / (1024 * 1024), 2)


class SystemSettings(models.Model):
    """إعدادات النظام"""
    SETTING_TYPES = [
        ('STRING', 'نص'),
        ('INTEGER', 'رقم صحيح'),
        ('FLOAT', 'رقم عشري'),
        ('BOOLEAN', 'صحيح/خطأ'),
        ('JSON', 'JSON'),
        ('FILE', 'ملف'),
    ]

    key = models.CharField(max_length=100, unique=True, verbose_name="مفتاح الإعداد")
    value = models.TextField(verbose_name="قيمة الإعداد")
    file_value = models.FileField(upload_to='company_files/', blank=True, null=True, verbose_name="ملف")
    value_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='STRING', verbose_name="نوع القيمة")

    # معلومات الإعداد
    category = models.CharField(max_length=50, verbose_name="الفئة")
    description = models.TextField(blank=True, verbose_name="الوصف")
    is_system = models.BooleanField(default=False, verbose_name="إعداد نظام")
    is_editable = models.BooleanField(default=True, verbose_name="قابل للتعديل")

    # تتبع التغييرات
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="حُدث بواسطة")

    class Meta:
        verbose_name = "إعداد نظام"
        verbose_name_plural = "إعدادات النظام"
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.category} - {self.key}"

    def get_value(self):
        """الحصول على القيمة بالنوع الصحيح"""
        if self.value_type == 'INTEGER':
            return int(self.value)
        elif self.value_type == 'FLOAT':
            return float(self.value)
        elif self.value_type == 'BOOLEAN':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.value_type == 'JSON':
            return json.loads(self.value)
        elif self.value_type == 'FILE':
            return self.file_value.url if self.file_value else None
        else:
            return self.value

    def set_value(self, value):
        """تعيين القيمة بالنوع الصحيح"""
        if self.value_type == 'JSON':
            self.value = json.dumps(value)
        else:
            self.value = str(value)


class LicenseInfo(models.Model):
    """معلومات الترخيص"""
    LICENSE_TYPES = [
        ('TRIAL', 'تجريبي'),
        ('BASIC', 'أساسي'),
        ('PROFESSIONAL', 'احترافي'),
        ('ENTERPRISE', 'مؤسسي'),
    ]

    license_key = models.CharField(max_length=100, unique=True, verbose_name="مفتاح الترخيص")
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPES, verbose_name="نوع الترخيص")

    # معلومات العميل
    customer_name = models.CharField(max_length=200, verbose_name="اسم العميل")
    customer_email = models.EmailField(verbose_name="بريد العميل")
    company_name = models.CharField(max_length=200, blank=True, verbose_name="اسم الشركة")

    # تواريخ الترخيص
    issued_date = models.DateTimeField(verbose_name="تاريخ الإصدار")
    expiry_date = models.DateTimeField(verbose_name="تاريخ الانتهاء")
    activation_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التفعيل")

    # حدود الترخيص
    max_users = models.IntegerField(default=1, verbose_name="الحد الأقصى للمستخدمين")
    max_branches = models.IntegerField(default=1, verbose_name="الحد الأقصى للفروع")
    max_transactions = models.IntegerField(null=True, blank=True, verbose_name="الحد الأقصى للمعاملات")

    # حالة الترخيص
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    is_trial = models.BooleanField(default=False, verbose_name="تجريبي")

    # معلومات إضافية
    features = models.JSONField(default=dict, verbose_name="المميزات المتاحة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "ترخيص"
        verbose_name_plural = "التراخيص"
        ordering = ['-issued_date']

    def __str__(self):
        return f"{self.customer_name} - {self.license_type}"

    @property
    def is_expired(self):
        """هل انتهى الترخيص"""
        return timezone.now() > self.expiry_date

    @property
    def days_remaining(self):
        """الأيام المتبقية"""
        if self.is_expired:
            return 0
        return (self.expiry_date - timezone.now()).days


class TaskbarSettings(models.Model):
    """إعدادات شريط المهام"""
    TASKBAR_POSITIONS = [
        ('NONE', 'بلا'),
        ('AUTO_HIDE', 'إخفاء تلقائي'),
        ('VERTICAL', 'رأسي'),
        ('HORIZONTAL', 'أفقي'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    position = models.CharField(max_length=20, choices=TASKBAR_POSITIONS, default='HORIZONTAL', verbose_name="موضع الشريط")
    auto_hide = models.BooleanField(default=False, verbose_name="إخفاء تلقائي")
    show_icons = models.BooleanField(default=True, verbose_name="إظهار الأيقونات")
    show_text = models.BooleanField(default=True, verbose_name="إظهار النص")

    # ترتيب العناصر
    menu_order = models.JSONField(default=list, verbose_name="ترتيب القوائم")
    pinned_items = models.JSONField(default=list, verbose_name="العناصر المثبتة")

    # إعدادات المظهر
    theme = models.CharField(max_length=20, default='default', verbose_name="المظهر")
    size = models.CharField(max_length=20, default='medium', verbose_name="الحجم")

    # تواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "إعدادات شريط المهام"
        verbose_name_plural = "إعدادات شريط المهام"

    def __str__(self):
        return f"{self.user.username} - {self.get_position_display()}"
