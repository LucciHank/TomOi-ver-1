from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_merge_20250211_1044'),  # Thay bằng migration cuối cùng của bạn
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='error_message',
            field=models.TextField(blank=True, null=True),
        ),
    ] 