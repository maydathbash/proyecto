from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0003_alter_chef_usuario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chef',
            name='usuario',
        ),
    ]
