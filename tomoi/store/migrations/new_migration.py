from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),  # Thay bằng migration cuối cùng của bạn
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='product',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='variants',
                to='store.product'
            ),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='base_price',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                default=0
            ),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='original_price',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='price_3_months',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='price_6_months',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='price_12_months',
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                null=True,
                blank=True
            ),
        ),
    ] 