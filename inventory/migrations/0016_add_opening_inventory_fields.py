# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_add_production_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='physicalinventory',
            name='financial_year',
            field=models.CharField(blank=True, max_length=10, verbose_name='السنة المالية'),
        ),
        migrations.AddField(
            model_name='physicalinventory',
            name='total_opening_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='إجمالي قيمة الافتتاح'),
        ),
        migrations.AlterField(
            model_name='physicalinventory',
            name='inventory_type',
            field=models.CharField(choices=[('FULL', 'جرد شامل'), ('PARTIAL', 'جرد جزئي'), ('CYCLE', 'جرد دوري'), ('SPOT', 'جرد عشوائي'), ('OPENING', 'جرد افتتاحي')], default='FULL', max_length=20, verbose_name='نوع الجرد'),
        ),
        migrations.AlterField(
            model_name='stockmovement',
            name='movement_type',
            field=models.CharField(choices=[('IN', 'إدخال'), ('OUT', 'إخراج'), ('TRANSFER', 'تحويل'), ('ADJUSTMENT', 'تسوية'), ('PRODUCTION', 'إنتاج'), ('OPENING', 'جرد افتتاحي')], max_length=20, verbose_name='نوع الحركة'),
        ),
    ]
