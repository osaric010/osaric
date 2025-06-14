# Generated by Django 5.2.2 on 2025-06-06 10:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('action', models.CharField(max_length=100, verbose_name='الإجراء')),
                ('model_name', models.CharField(max_length=100, verbose_name='اسم النموذج')),
                ('object_id', models.CharField(max_length=50, verbose_name='معرف الكائن')),
                ('object_repr', models.CharField(max_length=200, verbose_name='تمثيل الكائن')),
                ('changes', models.JSONField(default=dict, verbose_name='التغييرات')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='وكيل المستخدم')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'سجل النشاط',
                'verbose_name_plural': 'سجل الأنشطة',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DashboardWidget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('name', models.CharField(max_length=100, verbose_name='اسم الودجة')),
                ('widget_type', models.CharField(choices=[('CHART', 'رسم بياني'), ('COUNTER', 'عداد'), ('TABLE', 'جدول'), ('PROGRESS', 'شريط تقدم')], max_length=50, verbose_name='نوع الودجة')),
                ('position_x', models.IntegerField(default=0, verbose_name='الموضع الأفقي')),
                ('position_y', models.IntegerField(default=0, verbose_name='الموضع العمودي')),
                ('width', models.IntegerField(default=4, verbose_name='العرض')),
                ('height', models.IntegerField(default=3, verbose_name='الارتفاع')),
                ('config', models.JSONField(default=dict, verbose_name='إعدادات الودجة')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'ودجة لوحة التحكم',
                'verbose_name_plural': 'ودجات لوحة التحكم',
                'ordering': ['position_y', 'position_x'],
            },
        ),
        migrations.CreateModel(
            name='SystemAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('title', models.CharField(max_length=200, verbose_name='العنوان')),
                ('message', models.TextField(verbose_name='الرسالة')),
                ('alert_type', models.CharField(choices=[('INFO', 'معلومات'), ('WARNING', 'تحذير'), ('ERROR', 'خطأ'), ('SUCCESS', 'نجح')], default='INFO', max_length=20, verbose_name='نوع التنبيه')),
                ('is_read', models.BooleanField(default=False, verbose_name='مقروء')),
                ('expires_at', models.DateTimeField(blank=True, null=True, verbose_name='ينتهي في')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'تنبيه النظام',
                'verbose_name_plural': 'تنبيهات النظام',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('language', models.CharField(choices=[('ar', 'العربية'), ('en', 'English')], default='ar', max_length=10, verbose_name='اللغة')),
                ('theme', models.CharField(choices=[('light', 'فاتح'), ('dark', 'داكن')], default='light', max_length=20, verbose_name='المظهر')),
                ('dashboard_layout', models.JSONField(default=dict, verbose_name='تخطيط لوحة التحكم')),
                ('notifications_enabled', models.BooleanField(default=True, verbose_name='التنبيهات مفعلة')),
                ('email_notifications', models.BooleanField(default=True, verbose_name='تنبيهات البريد الإلكتروني')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'تفضيلات المستخدم',
                'verbose_name_plural': 'تفضيلات المستخدمين',
            },
        ),
    ]
