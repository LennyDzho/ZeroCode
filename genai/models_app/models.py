import uuid
from django.db import models

class Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    api_url = models.URLField()
    api_key = models.TextField()
    temperature = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    default_parameters = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return self.name
