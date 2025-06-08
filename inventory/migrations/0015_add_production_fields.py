# Generated manually for production fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0008_add_production_models'),
        ('inventory', '0013_openinginventory_openinginventoryitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='manufacturingorder',
            name='finished_goods_warehouse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='finished_production_orders', to='definitions.warehouse', verbose_name='مخزن الإنتاج التام'),
        ),
        migrations.AddField(
            model_name='manufacturingorder',
            name='labor_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='تكلفة العمالة'),
        ),
        migrations.AddField(
            model_name='manufacturingorder',
            name='operating_expenses',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='مصاريف التشغيل'),
        ),
        migrations.AddField(
            model_name='manufacturingorder',
            name='overhead_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='التكاليف العامة'),
        ),
    ]
