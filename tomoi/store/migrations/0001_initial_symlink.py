from django.db import migrations

class Migration(migrations.Migration):
    """
    Migration này chỉ là symbolic link đến migration thực sự
    để sửa lỗi references
    """
    
    replaces = [('store', '0001_initial')]
    
    dependencies = [
        # Không có dependencies
    ]

    operations = [
        # Không có operations
    ] 