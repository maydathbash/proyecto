from django.db import migrations, models


def limpiar_relaciones_antiguas(apps, schema_editor):
    ChefShowcooking = apps.get_model('cooking', 'Chef_ShowCooking')
    ChefRecetas = apps.get_model('cooking', 'Chef_Recetas')
    ChefShowcooking.objects.all().delete()
    ChefRecetas.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0003_remove_receta_ingredientes'),
        ('cuentas', '0004_remove_chef_usuario'),
    ]

    operations = [
        migrations.RunPython(limpiar_relaciones_antiguas, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='chef_recetas',
            name='id_chef',
            field=models.ForeignKey(on_delete=models.CASCADE, to='cuentas.chef'),
        ),
        migrations.AlterField(
            model_name='chef_showcooking',
            name='id_chef',
            field=models.ForeignKey(on_delete=models.CASCADE, to='cuentas.chef'),
        ),
    ]
