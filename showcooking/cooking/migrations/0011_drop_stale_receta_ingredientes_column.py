from django.db import migrations


def drop_stale_ingredientes_column(apps, schema_editor):
    connection = schema_editor.connection
    table_name = 'cooking_receta'

    with connection.cursor() as cursor:
        if connection.vendor == 'sqlite':
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = {row[1] for row in cursor.fetchall()}
        else:
            introspection = connection.introspection.get_table_description(cursor, table_name)
            existing_columns = {column.name for column in introspection}

    if 'ingredientes' not in existing_columns:
        return

    schema_editor.execute(f'ALTER TABLE {table_name} DROP COLUMN ingredientes')


class Migration(migrations.Migration):

    dependencies = [
        ('cooking', '0010_repair_bloque_preparacion_column'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(drop_stale_ingredientes_column, migrations.RunPython.noop),
            ],
            state_operations=[],
        ),
    ]