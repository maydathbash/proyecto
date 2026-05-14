from django.db import migrations


def add_missing_bloque_preparacion(apps, schema_editor):
    connection = schema_editor.connection
    table_name = 'cooking_ingredientes_receta'

    with connection.cursor() as cursor:
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {row[1] for row in cursor.fetchall()}

    if 'bloque_preparacion' in existing_columns:
        return

    IngredienteReceta = apps.get_model('cooking', 'ingredientes_receta')
    field = IngredienteReceta._meta.get_field('bloque_preparacion')
    field.set_attributes_from_name('bloque_preparacion')
    schema_editor.add_field(IngredienteReceta, field)


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0009_alter_ingredientes_options_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_missing_bloque_preparacion, migrations.RunPython.noop),
            ],
            state_operations=[],
        ),
    ]