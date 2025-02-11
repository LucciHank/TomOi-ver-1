from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(max_length=20, unique=True, default=''),
            preserve_default=False,
        ),
    ] 