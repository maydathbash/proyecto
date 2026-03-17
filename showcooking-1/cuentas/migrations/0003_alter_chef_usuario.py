from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0002_alter_chef_usuario_alter_rol_nombre_rol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chef',
            name='usuario',
            field=models.OneToOneField(on_delete=models.CASCADE, to='cuentas.Usuario'),
        ),
    ]