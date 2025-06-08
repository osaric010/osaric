# Generated manually to remove production models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0006_financialalert_finishedproduct_productionroute_and_more'),
    ]

    operations = [
        # Delete models in correct order to avoid foreign key constraints
        migrations.DeleteModel(
            name='ProductionStageRoute',
        ),
        migrations.DeleteModel(
            name='ProductionRoute',
        ),
        migrations.DeleteModel(
            name='FinishedProduct',
        ),
        migrations.DeleteModel(
            name='ProductionStage',
        ),
    ]
