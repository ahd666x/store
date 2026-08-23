from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_remove_deprecated_bom_fields'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Piece',
        ),
    ]
