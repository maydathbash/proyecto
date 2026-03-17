from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0002_alter_showcooking_imagen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receta',
            name='ingredientes',
        ),
    ]