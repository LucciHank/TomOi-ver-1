from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('category', models.CharField(choices=[('general', 'Chung'), ('account', 'Tài khoản'), ('payment', 'Thanh toán'), ('product', 'Sản phẩm'), ('technical', 'Kỹ thuật')], default='general', max_length=20)),
                ('status', models.CharField(choices=[('open', 'Đang mở'), ('in_progress', 'Đang xử lý'), ('closed', 'Đã đóng'), ('resolved', 'Đã giải quyết')], default='open', max_length=20)),
                ('is_customer_reply', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ] 