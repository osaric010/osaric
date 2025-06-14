# Generated by Django 5.2.2 on 2025-06-06 16:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0010_add_printer'),
        ('purchases', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EarnedDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('discount_number', models.CharField(max_length=50, unique=True, verbose_name='رقم الخصم')),
                ('date', models.DateField(verbose_name='التاريخ')),
                ('discount_type', models.CharField(choices=[('VOLUME', 'خصم الكمية'), ('PAYMENT_TERMS', 'خصم شروط الدفع'), ('SEASONAL', 'خصم موسمي'), ('LOYALTY', 'خصم الولاء'), ('PROMOTIONAL', 'خصم ترويجي'), ('EARLY_PAYMENT', 'خصم الدفع المبكر'), ('BULK_ORDER', 'خصم الطلبات الكبيرة'), ('OTHER', 'أخرى')], max_length=20, verbose_name='نوع الخصم')),
                ('discount_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='نسبة الخصم')),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='مبلغ الخصم')),
                ('base_amount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='المبلغ الأساسي')),
                ('minimum_quantity', models.DecimalField(blank=True, decimal_places=3, max_digits=15, null=True, verbose_name='الحد الأدنى للكمية')),
                ('minimum_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='الحد الأدنى للمبلغ')),
                ('payment_days', models.IntegerField(blank=True, null=True, verbose_name='أيام الدفع المبكر')),
                ('status', models.CharField(choices=[('PENDING', 'في الانتظار'), ('APPROVED', 'معتمد'), ('APPLIED', 'مطبق'), ('REJECTED', 'مرفوض'), ('EXPIRED', 'منتهي')], default='PENDING', max_length=20, verbose_name='الحالة')),
                ('valid_from', models.DateField(verbose_name='صالح من')),
                ('valid_until', models.DateField(blank=True, null=True, verbose_name='صالح حتى')),
                ('applied_date', models.DateField(blank=True, null=True, verbose_name='تاريخ التطبيق')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('notes', models.TextField(blank=True, verbose_name='ملاحظات')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('reference_invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='purchases.purchaseinvoice', verbose_name='الفاتورة المرجعية')),
                ('reference_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='purchases.purchaseorder', verbose_name='أمر الشراء المرجعي')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchases.supplier', verbose_name='المورد')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'خصم مكتسب',
                'verbose_name_plural': 'الخصومات المكتسبة',
                'ordering': ['-date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='EarnedDiscountItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=15, verbose_name='الكمية')),
                ('unit_cost', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='تكلفة الوحدة')),
                ('discount_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='نسبة الخصم')),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='مبلغ الخصم')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='إجمالي المبلغ')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('discount', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='purchases.earneddiscount', verbose_name='الخصم')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='definitions.item', verbose_name='الصنف')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL, verbose_name='حُدث بواسطة')),
            ],
            options={
                'verbose_name': 'صنف خصم مكتسب',
                'verbose_name_plural': 'أصناف الخصومات المكتسبة',
            },
        ),
    ]
