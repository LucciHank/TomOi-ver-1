from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_auto_20240128_update_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]