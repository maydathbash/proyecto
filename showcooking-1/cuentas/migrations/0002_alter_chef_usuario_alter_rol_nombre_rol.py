from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chef',
            name='usuario',
            field=models.OneToOneField(on_delete=models.CASCADE, to='cuentas.Usuario'),
        ),
        migrations.AlterField(
            model_name='rol',
            name='nombre_rol',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]