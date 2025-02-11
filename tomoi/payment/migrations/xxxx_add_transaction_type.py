from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),  # Thay bằng migration cuối cùng của bạn
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('purchase', 'Mua hàng'),
                    ('deposit', 'Nạp tiền')
                ],
                default='purchase'  # Mặc định là mua hàng
            ),
        ),
        migrations.AddField(
            model_name='transactionitem',
            name='variant_name',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='transactionitem',
            name='duration',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='transactionitem',
            name='upgrade_email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='transactionitem',
            name='account_username',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ] 