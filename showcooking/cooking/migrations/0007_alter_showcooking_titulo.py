from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0006_showcooking_visitas_receta_visitas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showcooking',
            name='titulo',
            field=models.CharField(max_length=120),
        ),
    ]