from rest_framework import serializers
from .models import Template, TemplateInstance

class TemplateSerializer(serializers.ModelSerializer):
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = ['id', 'name', 'template_type', 'template_type_display', 'description', 
                 'is_active', 'price', 'file_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        """Return file URL for system templates"""
        if obj.file:
            return obj.file.url
        return None

class TemplateInstanceSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_type = serializers.CharField(source='template.template_type', read_only=True)
    template_price = serializers.DecimalField(source='template.price', max_digits=10, decimal_places=2, read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateInstance
        fields = ['id', 'template', 'template_name', 'template_type', 'template_price',
                 'data', 'file_url', 'is_paid', 'stripe_session_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'template_name', 'template_type', 'template_price', 
                           'file_url', 'is_paid', 'stripe_session_id', 'created_at', 'updated_at']
    
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
    
    def validate_template(self, value):
        """Validate that template is active and available"""
        if not value.is_active:
            raise serializers.ValidationError("This template is not currently available")
        return value
    
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