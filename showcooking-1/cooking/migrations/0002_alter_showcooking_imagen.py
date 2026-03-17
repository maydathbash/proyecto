from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='showcooking',
            name='imagen',
            field=models.ImageField(upload_to='imagenes/recetas/', null=True, blank=True),
        ),
    ]