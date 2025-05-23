# Generated by Django 5.1.7 on 2025-03-08 10:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_rename_tcoin_customuser_tcoin_balance"),
        ("store", "0004_alter_orderitem_product"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tcoinhistory",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Lịch sử TCoin",
                "verbose_name_plural": "Lịch sử TCoin",
            },
        ),
        migrations.RemoveField(
            model_name="tcoinhistory",
            name="activity_type",
        ),
        migrations.AddField(
            model_name="tcoinhistory",
            name="balance_after",
            field=models.IntegerField(default=0, verbose_name="Số dư sau giao dịch"),
        ),
        migrations.AddField(
            model_name="tcoinhistory",
            name="transaction_type",
            field=models.CharField(
                choices=[
                    ("deposit", "Nạp tiền"),
                    ("withdraw", "Rút tiền"),
                    ("purchase", "Mua hàng"),
                    ("refund", "Hoàn tiền"),
                    ("bonus", "Thưởng"),
                    ("adjustment", "Điều chỉnh"),
                    ("checkin", "Điểm danh"),
                    ("referral", "Giới thiệu"),
                    ("other", "Khác"),
                ],
                default="adjustment",
                max_length=20,
                verbose_name="Loại giao dịch",
            ),
        ),
        migrations.AlterField(
            model_name="tcoinhistory",
            name="amount",
            field=models.IntegerField(default=0, verbose_name="Số lượng"),
        ),
        migrations.AlterField(
            model_name="tcoinhistory",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Thời gian"),
        ),
        migrations.AlterField(
            model_name="tcoinhistory",
            name="description",
            field=models.CharField(
                default="Điều chỉnh số dư", max_length=255, verbose_name="Mô tả"
            ),
        ),
        migrations.AlterField(
            model_name="tcoinhistory",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tcoin_history",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="PremiumSubscription",
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
                    "product_name",
                    models.CharField(max_length=100, verbose_name="Tên gói Premium"),
                ),
                ("duration", models.CharField(max_length=50, verbose_name="Thời hạn")),
                ("start_date", models.DateField(verbose_name="Ngày bắt đầu")),
                ("expiry_date", models.DateField(verbose_name="Ngày hết hạn")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("reminded", "Đã nhắc gia hạn"),
                            ("renewed", "Đã gia hạn"),
                            ("not_reminded", "Chưa nhắc gia hạn"),
                            ("no_renew", "Không gia hạn"),
                        ],
                        default="not_reminded",
                        max_length=30,
                        verbose_name="Trạng thái",
                    ),
                ),
                (
                    "reminder_sent",
                    models.BooleanField(default=False, verbose_name="Đã gửi nhắc nhở"),
                ),
                (
                    "reminder_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Ngày gửi nhắc nhở"
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="store.order",
                        verbose_name="Đơn hàng liên quan",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="premium_subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Gói Premium",
                "verbose_name_plural": "Các gói Premium",
                "ordering": ["expiry_date"],
            },
        ),
    ]
