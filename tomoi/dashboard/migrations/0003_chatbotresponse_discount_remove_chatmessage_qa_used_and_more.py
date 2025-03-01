# Generated manually to fix migration issues

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from datetime import timedelta

def add_timedelta(days=30):
    return django.utils.timezone.now() + timedelta(days=days)

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),  # Thay đổi từ 0002_auto_20230101_0000 thành 0001_initial
    ]

    operations = [
        migrations.CreateModel(
            name='ChatbotResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trigger', models.CharField(max_length=200)),
                ('response', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'Phần trăm'), ('fixed', 'Giảm trực tiếp')], default='percentage', max_length=20)),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_order_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('max_uses', models.IntegerField(default=0)),
                ('used_count', models.IntegerField(default=0)),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid_to', models.DateTimeField(default=add_timedelta)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        # Thêm các operations khác nếu cần
    ] 