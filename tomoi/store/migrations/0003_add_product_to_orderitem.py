from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(
                null=True,  # Cho phép null ban đầu
                on_delete=django.db.models.deletion.CASCADE,
                related_name='order_items',
                to='store.product'
            ),
        ),
    ] 