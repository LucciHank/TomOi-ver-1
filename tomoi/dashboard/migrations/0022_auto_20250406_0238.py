# Generated by Django 5.1.7 on 2025-04-06 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0021_source_is_active_alter_apiconfig_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='warrantyrequest',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Ngày hoàn thành'),
        ),
    ]
