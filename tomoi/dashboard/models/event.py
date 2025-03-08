from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#4e73df')  # Hex color code
    all_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time'] 