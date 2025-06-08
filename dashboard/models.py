from django.db import models
from django.contrib.auth.models import User
from definitions.models import BaseModel
from decimal import Decimal


class DashboardWidget(BaseModel):
    """ودجات لوحة التحكم"""
    name = models.CharField(max_length=100, verbose_name="اسم الودجة")
    widget_type = models.CharField(max_length=50, choices=[
        ('CHART', 'رسم بياني'),
        ('COUNTER', 'عداد'),
        ('TABLE', 'جدول'),
        ('PROGRESS', 'شريط تقدم'),
    ], verbose_name="نوع الودجة")
    position_x = models.IntegerField(default=0, verbose_name="الموضع الأفقي")
    position_y = models.IntegerField(default=0, verbose_name="الموضع العمودي")
    width = models.IntegerField(default=4, verbose_name="العرض")
    height = models.IntegerField(default=3, verbose_name="الارتفاع")
    config = models.JSONField(default=dict, verbose_name="إعدادات الودجة")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")

    class Meta:
        verbose_name = "ودجة لوحة التحكم"
        verbose_name_plural = "ودجات لوحة التحكم"
        ordering = ['position_y', 'position_x']

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class SystemAlert(BaseModel):
    """تنبيهات النظام"""
    title = models.CharField(max_length=200, verbose_name="العنوان")
    message = models.TextField(verbose_name="الرسالة")
    alert_type = models.CharField(max_length=20, choices=[
        ('INFO', 'معلومات'),
        ('WARNING', 'تحذير'),
        ('ERROR', 'خطأ'),
        ('SUCCESS', 'نجح'),
    ], default='INFO', verbose_name="نوع التنبيه")
    is_read = models.BooleanField(default=False, verbose_name="مقروء")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="ينتهي في")

    class Meta:
        verbose_name = "تنبيه النظام"
        verbose_name_plural = "تنبيهات النظام"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class UserPreference(BaseModel):
    """تفضيلات المستخدم"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    language = models.CharField(max_length=10, choices=[
        ('ar', 'العربية'),
        ('en', 'English'),
    ], default='ar', verbose_name="اللغة")
    theme = models.CharField(max_length=20, choices=[
        ('light', 'فاتح'),
        ('dark', 'داكن'),
    ], default='light', verbose_name="المظهر")
    dashboard_layout = models.JSONField(default=dict, verbose_name="تخطيط لوحة التحكم")
    notifications_enabled = models.BooleanField(default=True, verbose_name="التنبيهات مفعلة")
    email_notifications = models.BooleanField(default=True, verbose_name="تنبيهات البريد الإلكتروني")

    class Meta:
        verbose_name = "تفضيلات المستخدم"
        verbose_name_plural = "تفضيلات المستخدمين"

    def __str__(self):
        return f"تفضيلات {self.user.username}"


class ActivityLog(BaseModel):
    """سجل الأنشطة"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    action = models.CharField(max_length=100, verbose_name="الإجراء")
    model_name = models.CharField(max_length=100, verbose_name="اسم النموذج")
    object_id = models.CharField(max_length=50, verbose_name="معرف الكائن")
    object_repr = models.CharField(max_length=200, verbose_name="تمثيل الكائن")
    changes = models.JSONField(default=dict, verbose_name="التغييرات")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    user_agent = models.TextField(blank=True, verbose_name="وكيل المستخدم")

    class Meta:
        verbose_name = "سجل النشاط"
        verbose_name_plural = "سجل الأنشطة"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name}"
