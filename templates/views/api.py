from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from ..serializers import (
    TemplateSerializer, 
    TemplateInstanceSerializer, 
    CreateInstanceSerializer,
    EmailRequestSerializer
)
from ..models import Template, TemplateInstance
from ..services.pdf_service import PDFGenerationService
from ..services.stripe_service import StripeService
from ..services.email_service import EmailService

class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for browsing available system templates (read-only for users)"""
    serializer_class = TemplateSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['template_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['template_type', 'name']
    
    def get_queryset(self):
        """Only show active templates to users"""
        return Template.objects.filter(is_active=True)

class TemplateInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing template instances"""
    queryset = TemplateInstance.objects.all()
    serializer_class = TemplateInstanceSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [AllowAny]  # Guest access
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['template__template_type', 'is_paid']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateInstanceSerializer
        return TemplateInstanceSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a template instance, generate PDF, and create Stripe checkout"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Create template instance
            template_instance = serializer.save()
            
            # Generate PDF
            pdf_url = PDFGenerationService.generate_pdf(template_instance)
            
            # Create Stripe checkout session
            stripe_service = StripeService()
            checkout_data = stripe_service.create_checkout_session(template_instance, request)
            
            return Response({
                'instance_id': str(template_instance.id),
                'checkout_url': checkout_data['checkout_url'],
                'message': 'PDF generated successfully. Please complete payment to download.'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Send generated PDF to email (only if paid)"""
        template_instance = self.get_object()
        
        if not template_instance.is_paid:
            return Response({
                'error': 'Payment not completed. Please complete payment first.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = EmailRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            email = serializer.validated_data['email']
            EmailService.send_download_link_email(template_instance, email)
            
            return Response({
                'success': True,
                'message': f'PDF download link sent to {email}'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the generated PDF (only if paid)"""
        template_instance = self.get_object()
        
        if not template_instance.is_paid:
            return Response({
                'error': 'Payment not completed. Please complete payment first.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not template_instance.file:
            return Response({
                'error': 'PDF file not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # For S3, redirect to the file URL
        if template_instance.file.url:
            return Response({
                'download_url': template_instance.file.url
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'File not accessible'
        }, status=status.HTTP_404_NOT_FOUND) 