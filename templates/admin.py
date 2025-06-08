from django.contrib import admin
from .models import Template, TemplateInstance

admin.site.register(Template)
admin.site.register(TemplateInstance)