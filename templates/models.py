import uuid
from django.db import models
from django.utils import timezone

class Template(models.Model):
    TEMPLATE_TYPES = [
        ('paystub', 'Paystub'),
        ('w2', 'W-2 Form'),
        ('1099', '1099 Form'),
        ('invoice', 'Invoice'),
        ('receipt', 'Receipt'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, default='other')
    file = models.FileField(upload_to='system-templates/')  # Required field for system templates
    preview_file = models.FileField(upload_to='system-templates/previews/', blank=True, null=True, help_text='PDF template for preview generation')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)  # Whether template is available for use
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Price for generating instances
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['template_type', 'name']

    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"

class TemplateInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='instances')
    data = models.JSONField(blank=True, null=True)  # Allow null values
    file = models.FileField(upload_to='template-instances/', blank=True)
    is_paid = models.BooleanField(default=False)  # Track payment status
    stripe_session_id = models.CharField(max_length=255, blank=True)  # Stripe checkout session ID
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Instance of {self.template.name} - {self.created_at}"

class TemplatePreview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='previews')
    data = models.JSONField(blank=True, null=True)
    file = models.FileField(upload_to='template-previews/', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preview of {self.template.name} - {self.created_at}"