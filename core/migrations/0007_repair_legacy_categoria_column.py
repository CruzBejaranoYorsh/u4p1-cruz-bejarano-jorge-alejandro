from django.db import migrations


def repair_legacy_categoria_column(apps, schema_editor):
    connection = schema_editor.connection
    table_name = 'core_servicio'

    with connection.cursor() as cursor:
        table_names = {
            table.name for table in connection.introspection.get_table_list(cursor)
        }
        if table_name not in table_names:
            return

        columns = {
            column.name
            for column in connection.introspection.get_table_description(
                cursor, table_name
            )
        }
        service_model = apps.get_model('core', 'Servicio')
        categoria_field = service_model._meta.get_field('categoria')
        if 'categoria' not in columns:
            schema_editor.add_field(service_model, categoria_field)
            columns.add('categoria')

        if 'categoria_id' not in columns or 'core_categoria' not in table_names:
            return

        quote = schema_editor.quote_name
        service_table = quote(table_name)
        categoria_table = quote('core_categoria')
        cursor.execute(
            f'UPDATE {service_table} '
            f'SET {quote("categoria")} = ('
            f'SELECT {quote("nombre")} FROM {categoria_table} '
            f'WHERE {categoria_table}.{quote("id")} = '
            f'{service_table}.{quote("categoria_id")}) '
            f'WHERE {quote("categoria_id")} IS NOT NULL '
            f'AND {quote("categoria")} = %s',
            [''],
        )


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            repair_legacy_categoria_column,
            migrations.RunPython.noop,
        ),
    ]
