from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),  # Thay thế bằng migration trước đó
    ]

    operations = [
        migrations.CreateModel(
            name='APIConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_type', models.CharField(choices=[('gemini', 'Google Gemini AI'), ('openai', 'OpenAI'), ('anthropic', 'Anthropic'), ('cohere', 'Cohere')], default='gemini', max_length=20)),
                ('api_key', models.CharField(max_length=255)),
                ('model', models.CharField(default='gemini-pro', max_length=100)),
                ('temperature', models.FloatField(default=0.7)),
                ('max_tokens', models.IntegerField(default=2048)),
                ('endpoint', models.CharField(blank=True, max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Cấu hình API',
                'verbose_name_plural': 'Cấu hình API',
            },
        ),
    ] 