# Generated by Django 5.2.2 on 2025-06-06 12:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0003_assetgroup'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='كود الشخص/الجهة')),
                ('name', models.CharField(max_length=200, verbose_name='الاسم')),
                ('name_english', models.CharField(blank=True, max_length=200, verbose_name='الاسم بالإنجليزية')),
                ('person_type', models.CharField(choices=[('CUSTOMER', 'عميل'), ('SUPPLIER', 'مورد'), ('EMPLOYEE', 'موظف'), ('BOTH', 'عميل ومورد'), ('BANK', 'بنك'), ('GOVERNMENT', 'جهة حكومية'), ('PARTNER', 'شريك'), ('OTHER', 'أخرى')], default='CUSTOMER', max_length=20, verbose_name='نوع الشخص/الجهة')),
                ('entity_type', models.CharField(choices=[('INDIVIDUAL', 'فرد'), ('COMPANY', 'شركة'), ('INSTITUTION', 'مؤسسة'), ('GOVERNMENT', 'جهة حكومية')], default='INDIVIDUAL', max_length=20, verbose_name='نوع الكيان')),
                ('national_id', models.CharField(blank=True, max_length=20, verbose_name='رقم الهوية/السجل التجاري')),
                ('tax_number', models.CharField(blank=True, max_length=20, verbose_name='الرقم الضريبي')),
                ('commercial_register', models.CharField(blank=True, max_length=20, verbose_name='السجل التجاري')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='الهاتف')),
                ('mobile', models.CharField(blank=True, max_length=20, verbose_name='الجوال')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='البريد الإلكتروني')),
                ('website', models.URLField(blank=True, verbose_name='الموقع الإلكتروني')),
                ('address', models.TextField(blank=True, verbose_name='العنوان')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='المدينة')),
                ('state', models.CharField(blank=True, max_length=100, verbose_name='المحافظة/المنطقة')),
                ('country', models.CharField(default='مصر', max_length=100, verbose_name='الدولة')),
                ('postal_code', models.CharField(blank=True, max_length=10, verbose_name='الرمز البريدي')),
                ('credit_limit', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='حد الائتمان')),
                ('payment_terms', models.IntegerField(blank=True, null=True, verbose_name='مدة السداد (أيام)')),
                ('account_receivable', models.CharField(blank=True, max_length=20, verbose_name='حساب المدينين')),
                ('account_payable', models.CharField(blank=True, max_length=20, verbose_name='حساب الدائنين')),
                ('contact_person', models.CharField(blank=True, max_length=100, verbose_name='الشخص المسؤول')),
                ('contact_title', models.CharField(blank=True, max_length=100, verbose_name='المنصب')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('is_active_customer', models.BooleanField(default=True, verbose_name='عميل نشط')),
                ('is_active_supplier', models.BooleanField(default=False, verbose_name='مورد نشط')),
                ('allow_credit', models.BooleanField(default=True, verbose_name='السماح بالائتمان')),
                ('registration_date', models.DateField(blank=True, null=True, verbose_name='تاريخ التسجيل')),
                ('last_transaction_date', models.DateField(blank=True, null=True, verbose_name='تاريخ آخر معاملة')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('currency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='definitions.currency', verbose_name='العملة الافتراضية')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'شخص/جهة',
                'verbose_name_plural': 'الأشخاص والجهات',
                'ordering': ['name'],
            },
        ),
    ]
