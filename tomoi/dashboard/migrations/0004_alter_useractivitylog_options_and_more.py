# Generated by Django 5.1.4 on 2025-03-07 11:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0003_useractivitylog"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="useractivitylog",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Nhật ký hoạt động",
                "verbose_name_plural": "Nhật ký hoạt động",
            },
        ),
        migrations.AddField(
            model_name="useractivitylog",
            name="metadata",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="useractivitylog",
            name="action_type",
            field=models.CharField(
                choices=[
                    ("create", "tạo mới"),
                    ("update", "cập nhật"),
                    ("delete", "xóa"),
                    ("restore", "khôi phục"),
                    ("permission", "phân quyền"),
                ],
                max_length=20,
            ),
        ),
    ]
