# Generated by Django 5.2.2 on 2025-06-06 13:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0004_person'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='كود فئة المصروف')),
                ('name', models.CharField(max_length=100, verbose_name='اسم فئة المصروف')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('category', models.CharField(choices=[('OPERATIONAL', 'مصروفات تشغيلية'), ('ADMINISTRATIVE', 'مصروفات إدارية'), ('SELLING', 'مصروفات بيعية'), ('FINANCIAL', 'مصروفات مالية'), ('CAPITAL', 'مصروفات رأسمالية'), ('OTHER', 'أخرى')], default='OPERATIONAL', max_length=20, verbose_name='تصنيف المصروف')),
                ('default_account', models.CharField(blank=True, max_length=20, verbose_name='الحساب الافتراضي')),
                ('requires_approval', models.BooleanField(default=False, verbose_name='يتطلب موافقة')),
                ('max_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='الحد الأقصى للمبلغ')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'فئة مصروف',
                'verbose_name_plural': 'فئات المصروفات',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ExpenseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='كود بند المصروف')),
                ('name', models.CharField(max_length=100, verbose_name='اسم بند المصروف')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('account_number', models.CharField(blank=True, max_length=20, verbose_name='رقم الحساب')),
                ('is_recurring', models.BooleanField(default=False, verbose_name='مصروف دوري')),
                ('recurring_period', models.CharField(blank=True, choices=[('DAILY', 'يومي'), ('WEEKLY', 'أسبوعي'), ('MONTHLY', 'شهري'), ('QUARTERLY', 'ربع سنوي'), ('YEARLY', 'سنوي')], max_length=20, verbose_name='فترة التكرار')),
                ('min_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='الحد الأدنى للمبلغ')),
                ('max_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='الحد الأقصى للمبلغ')),
                ('requires_document', models.BooleanField(default=True, verbose_name='يتطلب مستند')),
                ('requires_approval', models.BooleanField(default=False, verbose_name='يتطلب موافقة')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('expense_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='definitions.expensecategory', verbose_name='فئة المصروف')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'بند مصروف',
                'verbose_name_plural': 'بنود المصروفات',
                'ordering': ['expense_category', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RevenueCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='كود فئة الإيراد')),
                ('name', models.CharField(max_length=100, verbose_name='اسم فئة الإيراد')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('category', models.CharField(choices=[('SALES', 'إيرادات مبيعات'), ('SERVICES', 'إيرادات خدمات'), ('INVESTMENT', 'إيرادات استثمارية'), ('FINANCIAL', 'إيرادات مالية'), ('RENTAL', 'إيرادات إيجارات'), ('OTHER', 'أخرى')], default='SALES', max_length=20, verbose_name='تصنيف الإيراد')),
                ('default_account', models.CharField(blank=True, max_length=20, verbose_name='الحساب الافتراضي')),
                ('is_taxable', models.BooleanField(default=True, verbose_name='خاضع للضريبة')),
                ('tax_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='معدل الضريبة (%)')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'فئة إيراد',
                'verbose_name_plural': 'فئات الإيرادات',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RevenueItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='كود بند الإيراد')),
                ('name', models.CharField(max_length=100, verbose_name='اسم بند الإيراد')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('account_number', models.CharField(blank=True, max_length=20, verbose_name='رقم الحساب')),
                ('is_recurring', models.BooleanField(default=False, verbose_name='إيراد دوري')),
                ('recurring_period', models.CharField(blank=True, choices=[('DAILY', 'يومي'), ('WEEKLY', 'أسبوعي'), ('MONTHLY', 'شهري'), ('QUARTERLY', 'ربع سنوي'), ('YEARLY', 'سنوي')], max_length=20, verbose_name='فترة التكرار')),
                ('is_taxable', models.BooleanField(default=True, verbose_name='خاضع للضريبة')),
                ('tax_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='معدل الضريبة (%)')),
                ('min_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='الحد الأدنى للمبلغ')),
                ('max_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='الحد الأقصى للمبلغ')),
                ('requires_contract', models.BooleanField(default=False, verbose_name='يتطلب عقد')),
                ('commission_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='معدل العمولة (%)')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('revenue_category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='definitions.revenuecategory', verbose_name='فئة الإيراد')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'بند إيراد',
                'verbose_name_plural': 'بنود الإيرادات',
                'ordering': ['revenue_category', 'name'],
            },
        ),
    ]
