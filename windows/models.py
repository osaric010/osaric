from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class WindowCategory(models.Model):
    """فئات النوافذ"""
    CATEGORY_CHOICES = [
        ('sales', 'نوافذ المبيعات'),
        ('purchases', 'نوافذ المشتريات'),
        ('inventory', 'نوافذ المخازن'),
        ('accounting', 'نوافذ المحاسبة'),
        ('persons', 'نوافذ الأشخاص'),
        ('assets', 'نوافذ الأصول الثابتة'),
        ('payroll', 'نوافذ الرواتب'),
        ('branches', 'نوافذ الفروع'),
        ('tools', 'نوافذ متنوعة'),
    ]

    name = models.CharField(max_length=100, verbose_name='اسم الفئة')
    code = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True, verbose_name='رمز الفئة')
    icon = models.CharField(max_length=50, default='fas fa-window-maximize', verbose_name='أيقونة الفئة')
    color = models.CharField(max_length=20, default='primary', verbose_name='لون الفئة')
    order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    is_active = models.BooleanField(default=True, verbose_name='نشط')

    class Meta:
        verbose_name = 'فئة النوافذ'
        verbose_name_plural = 'فئات النوافذ'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class WindowDefinition(models.Model):
    """تعريف النوافذ"""
    WINDOW_TYPES = [
        ('form', 'نموذج إدخال'),
        ('list', 'قائمة عرض'),
        ('report', 'تقرير'),
        ('tool', 'أداة'),
        ('calculator', 'آلة حاسبة'),
        ('calendar', 'تقويم'),
        ('notepad', 'مفكرة'),
    ]

    name = models.CharField(max_length=100, verbose_name='اسم النافذة')
    code = models.CharField(max_length=50, unique=True, verbose_name='رمز النافذة')
    category = models.ForeignKey(WindowCategory, on_delete=models.CASCADE, verbose_name='الفئة')
    window_type = models.CharField(max_length=20, choices=WINDOW_TYPES, default='form', verbose_name='نوع النافذة')
    icon = models.CharField(max_length=50, default='fas fa-file', verbose_name='أيقونة النافذة')
    url = models.CharField(max_length=200, blank=True, null=True, verbose_name='رابط النافذة')
    description = models.TextField(blank=True, null=True, verbose_name='وصف النافذة')
    shortcut_key = models.CharField(max_length=20, blank=True, null=True, verbose_name='اختصار لوحة المفاتيح')
    order = models.IntegerField(default=0, verbose_name='ترتيب العرض')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    requires_permission = models.CharField(max_length=100, blank=True, null=True, verbose_name='صلاحية مطلوبة')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'تعريف النافذة'
        verbose_name_plural = 'تعريفات النوافذ'
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class UserWindowPreference(models.Model):
    """تفضيلات المستخدم للنوافذ"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    window = models.ForeignKey(WindowDefinition, on_delete=models.CASCADE, verbose_name='النافذة')
    is_favorite = models.BooleanField(default=False, verbose_name='مفضلة')
    is_pinned = models.BooleanField(default=False, verbose_name='مثبتة')
    custom_shortcut = models.CharField(max_length=20, blank=True, null=True, verbose_name='اختصار مخصص')
    last_used = models.DateTimeField(blank=True, null=True, verbose_name='آخر استخدام')
    usage_count = models.IntegerField(default=0, verbose_name='عدد مرات الاستخدام')

    class Meta:
        verbose_name = 'تفضيلات النوافذ'
        verbose_name_plural = 'تفضيلات النوافذ'
        unique_together = ['user', 'window']

    def __str__(self):
        return f"{self.user.username} - {self.window.name}"


class OpenWindow(models.Model):
    """النوافذ المفتوحة حالياً"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    window = models.ForeignKey(WindowDefinition, on_delete=models.CASCADE, verbose_name='النافذة')
    session_key = models.CharField(max_length=100, verbose_name='مفتاح الجلسة')
    window_instance_id = models.CharField(max_length=50, verbose_name='معرف النافذة')
    title = models.CharField(max_length=200, verbose_name='عنوان النافذة')
    url = models.CharField(max_length=500, verbose_name='رابط النافذة')
    position_x = models.IntegerField(default=100, verbose_name='موضع X')
    position_y = models.IntegerField(default=100, verbose_name='موضع Y')
    width = models.IntegerField(default=800, verbose_name='العرض')
    height = models.IntegerField(default=600, verbose_name='الارتفاع')
    is_maximized = models.BooleanField(default=False, verbose_name='مكبرة')
    is_minimized = models.BooleanField(default=False, verbose_name='مصغرة')
    z_index = models.IntegerField(default=1000, verbose_name='ترتيب العمق')
    opened_at = models.DateTimeField(auto_now_add=True, verbose_name='وقت الفتح')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='آخر نشاط')

    class Meta:
        verbose_name = 'النافذة المفتوحة'
        verbose_name_plural = 'النوافذ المفتوحة'
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class WindowTemplate(models.Model):
    """قوالب النوافذ"""
    name = models.CharField(max_length=100, verbose_name='اسم القالب')
    window_type = models.CharField(max_length=20, choices=WindowDefinition.WINDOW_TYPES, verbose_name='نوع النافذة')
    html_template = models.TextField(verbose_name='قالب HTML')
    css_styles = models.TextField(blank=True, null=True, verbose_name='أنماط CSS')
    javascript_code = models.TextField(blank=True, null=True, verbose_name='كود JavaScript')
    default_width = models.IntegerField(default=800, verbose_name='العرض الافتراضي')
    default_height = models.IntegerField(default=600, verbose_name='الارتفاع الافتراضي')
    is_resizable = models.BooleanField(default=True, verbose_name='قابل لتغيير الحجم')
    is_draggable = models.BooleanField(default=True, verbose_name='قابل للسحب')
    has_close_button = models.BooleanField(default=True, verbose_name='زر إغلاق')
    has_minimize_button = models.BooleanField(default=True, verbose_name='زر تصغير')
    has_maximize_button = models.BooleanField(default=True, verbose_name='زر تكبير')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'قالب النافذة'
        verbose_name_plural = 'قوالب النوافذ'
        ordering = ['name']

    def __str__(self):
        return self.name


class QuickAccess(models.Model):
    """الوصول السريع للنوافذ"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='المستخدم')
    window = models.ForeignKey(WindowDefinition, on_delete=models.CASCADE, verbose_name='النافذة')
    position = models.IntegerField(default=0, verbose_name='الموضع')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإضافة')

    class Meta:
        verbose_name = 'الوصول السريع'
        verbose_name_plural = 'الوصول السريع'
        unique_together = ['user', 'window']
        ordering = ['position']

    def __str__(self):
        return f"{self.user.username} - {self.window.name}"
