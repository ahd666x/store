from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_seed_product_categories'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='categories/', verbose_name='تصویر دسته'),
        ),
    ]
