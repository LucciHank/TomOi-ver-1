# Generated by Django 5.1.7 on 2025-04-09 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_alter_order_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sold_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Số lượng đã bán'),
        ),
        migrations.AlterField(
            model_name='product',
            name='requires_account_password',
            field=models.BooleanField(default=False, verbose_name='Yêu cầu Tài khoản & Mật khẩu'),
        ),
        migrations.AlterField(
            model_name='product',
            name='requires_email',
            field=models.BooleanField(default=False, verbose_name='Yêu cầu Email'),
        ),
    ]
