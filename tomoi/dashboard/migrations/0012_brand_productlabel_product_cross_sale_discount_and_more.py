# Generated by Django 5.1.7 on 2025-03-16 12:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0011_sourcehistory_account_password_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Brand",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="brands/")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Thương hiệu",
                "verbose_name_plural": "Thương hiệu",
            },
        ),
        migrations.CreateModel(
            name="ProductLabel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("color", models.CharField(default="primary", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Nhãn sản phẩm",
                "verbose_name_plural": "Nhãn sản phẩm",
            },
        ),
        migrations.AddField(
            model_name="product",
            name="cross_sale_discount",
            field=models.IntegerField(
                default=0, help_text="Phần trăm giảm giá khi mua kèm"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="cross_sale_products",
            field=models.ManyToManyField(blank=True, to="dashboard.product"),
        ),
        migrations.AddField(
            model_name="product",
            name="duration",
            field=models.CharField(
                choices=[
                    ("1_DAY", "1 ngày"),
                    ("1_WEEK", "1 tuần"),
                    ("1_MONTH", "1 tháng"),
                    ("3_MONTHS", "3 tháng"),
                    ("6_MONTHS", "6 tháng"),
                    ("12_MONTHS", "1 năm"),
                ],
                default="1_MONTH",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="features",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="product",
            name="is_cross_sale",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="is_featured",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="product",
            name="old_price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="product_code",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="requires_account_password",
            field=models.BooleanField(
                default=False,
                help_text="Khách hàng cần cung cấp tài khoản và mật khẩu để nâng cấp",
                verbose_name="Yêu cầu Tài khoản & Mật khẩu",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="requires_email",
            field=models.BooleanField(
                default=False,
                help_text="Khách hàng cần cung cấp email để nâng cấp",
                verbose_name="Yêu cầu Email",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="stock",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="product",
            name="brand",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="products",
                to="dashboard.brand",
            ),
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="categories/"),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="dashboard.category",
                    ),
                ),
            ],
            options={
                "verbose_name": "Danh mục",
                "verbose_name_plural": "Danh mục",
            },
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="products",
                to="dashboard.category",
            ),
        ),
        migrations.CreateModel(
            name="ProductChangeLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("create", "Tạo mới"),
                            ("update", "Cập nhật"),
                            ("delete", "Xóa"),
                            ("status_change", "Thay đổi trạng thái"),
                        ],
                        max_length=20,
                    ),
                ),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="change_logs",
                        to="dashboard.product",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Lịch sử thay đổi sản phẩm",
                "verbose_name_plural": "Lịch sử thay đổi sản phẩm",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="products/")),
                ("is_primary", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="dashboard.product",
                    ),
                ),
            ],
            options={
                "verbose_name": "Hình ảnh sản phẩm",
                "verbose_name_plural": "Hình ảnh sản phẩm",
            },
        ),
        migrations.AddField(
            model_name="product",
            name="label",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="dashboard.productlabel",
            ),
        ),
    ]
