# Generated by Django 5.1.7 on 2025-03-15 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_sourcehistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcehistory',
            name='account_password',
            field=models.CharField(blank=True, max_length=255, verbose_name='Mật khẩu'),
        ),
        migrations.AddField(
            model_name='sourcehistory',
            name='account_type',
            field=models.CharField(blank=True, choices=[('new_account', 'Tài khoản cấp mới'), ('upgrade', 'Up chính chủ'), ('activation_code', 'Code kích hoạt'), ('other', 'Khác')], default='new_account', max_length=20, verbose_name='Hình thức nhập'),
        ),
        migrations.AddField(
            model_name='sourcehistory',
            name='account_username',
            field=models.CharField(blank=True, max_length=255, verbose_name='Tài khoản chính chủ'),
        ),
        migrations.AddField(
            model_name='sourcehistory',
            name='products',
            field=models.JSONField(blank=True, default=list, verbose_name='Danh sách sản phẩm'),
        ),
    ]
