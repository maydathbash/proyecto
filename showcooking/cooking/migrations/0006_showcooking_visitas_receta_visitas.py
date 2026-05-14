from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0005_alter_receta_categoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='receta',
            name='visitas',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='showcooking',
            name='visitas',
            field=models.PositiveIntegerField(default=0),
        ),
    ]