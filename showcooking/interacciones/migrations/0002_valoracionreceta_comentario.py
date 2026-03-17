from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interacciones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='valoracionreceta',
            name='comentario',
            field=models.TextField(blank=True),
        ),
    ]
