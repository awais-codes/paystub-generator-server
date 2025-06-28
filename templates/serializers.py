from rest_framework import serializers
from .models import Template, TemplateInstance

class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = '__all__'

class TemplateInstanceSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateInstance
        fields = '__all__'
    
    def get_file_url(self, obj):
        """Return file URL only if payment is completed"""
        if obj.is_paid and obj.file:
            return obj.file.url
        return None

class CreateInstanceSerializer(serializers.ModelSerializer):
    """Serializer for creating template instances with data"""
    
    class Meta:
        model = TemplateInstance
        fields = ['template', 'data']
    
    def validate_data(self, value):
        """Validate that data is a dictionary"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data must be a dictionary")
        return value

class EmailRequestSerializer(serializers.Serializer):
    """Serializer for email delivery requests"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Basic email validation"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Please provide a valid email address")
        return value