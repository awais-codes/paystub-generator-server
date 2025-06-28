import uuid
from django.db import models
from django.utils import timezone

class Template(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='templates/', blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TemplateInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='instances')
    data = models.JSONField(blank=True, null=True)  # Allow null values
    file = models.FileField(upload_to='templates-instances/', blank=True)
    is_paid = models.BooleanField(default=False)  # Track payment status
    stripe_session_id = models.CharField(max_length=255, blank=True)  # Stripe checkout session ID
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Instance of {self.template.name} - {self.created_at}"