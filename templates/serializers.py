from rest_framework import serializers
from .models import Template, TemplateInstance

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'

class TemplateInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateInstance
        fields = '__all__'