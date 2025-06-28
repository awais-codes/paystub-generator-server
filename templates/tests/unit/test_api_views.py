import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.base import ContentFile
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from templates.models import Template, TemplateInstance
from templates.services.pdf_service import PDFGenerationService
from templates.services.stripe_service import StripeService
from templates.services.email_service import EmailService
from .test_utils import create_test_pdf_content


class TemplateViewSetTestCase(TestCase):
    """Test cases for TemplateViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Test Template",
            description="A test template"
        )
    
    def test_list_templates(self):
        """Test listing all templates"""
        url = reverse('template-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Template")
    
    def test_create_template(self):
        """Test creating a new template"""
        url = reverse('template-list')
        data = {
            'name': 'New Template',
            'description': 'A new template'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Template.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Template')
    
    def test_create_template_with_file(self):
        """Test creating a template with PDF file"""
        url = reverse('template-list')
        
        # Create a test PDF file using SimpleUploadedFile
        pdf_content = create_test_pdf_content()
        
        data = {
            'name': 'Template with File',
            'description': 'Template with PDF file',
            'file': SimpleUploadedFile('test_template.pdf', pdf_content, content_type='application/pdf')
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Template.objects.count(), 2)
        self.assertIsNotNone(response.data['file'])
    
    def test_retrieve_template(self):
        """Test retrieving a specific template"""
        url = reverse('template-detail', kwargs={'pk': self.template.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Template")
    
    def test_update_template(self):
        """Test updating a template"""
        url = reverse('template-detail', kwargs={'pk': self.template.id})
        data = {
            'name': 'Updated Template',
            'description': 'Updated description'
        }
        
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.template.refresh_from_db()
        self.assertEqual(self.template.name, 'Updated Template')
    
    def test_delete_template(self):
        """Test deleting a template"""
        url = reverse('template-detail', kwargs={'pk': self.template.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Template.objects.count(), 0)


class TemplateInstanceViewSetTestCase(TestCase):
    """Test cases for TemplateInstanceViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Test Template",
            description="A test template"
        )
        
        # Create a test PDF file for the template
        pdf_content = create_test_pdf_content()
        self.template.file.save('test_template.pdf', ContentFile(pdf_content))
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "John Doe", "SSN": "123-45-6789"}
        )
    
    @patch('templates.services.pdf_service.PDFGenerationService.generate_pdf')
    @patch('templates.services.stripe_service.StripeService.create_checkout_session')
    def test_create_instance_success(self, mock_stripe, mock_pdf):
        """Test creating a template instance successfully"""
        url = reverse('template-instance-list')
        data = {
            'template': self.template.id,
            'data': {
                'EmployeeName': 'Jane Smith',
                'SSN': '987-65-4321'
            }
        }
        
        # Mock PDF generation
        mock_pdf.return_value = "https://s3.amazonaws.com/bucket/test.pdf"
        
        # Mock Stripe checkout session
        mock_stripe.return_value = {
            'session_id': 'cs_test_123',
            'checkout_url': 'https://checkout.stripe.com/pay/cs_test_123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TemplateInstance.objects.count(), 2)
        
        # Verify response contains expected data
        self.assertIn('instance_id', response.data)
        self.assertIn('checkout_url', response.data)
        self.assertIn('message', response.data)
        
        # Verify PDF generation was called
        mock_pdf.assert_called_once()
        
        # Verify Stripe checkout was created
        mock_stripe.assert_called_once()
    
    def test_create_instance_invalid_data(self):
        """Test creating instance with invalid data"""
        url = reverse('template-instance-list')
        data = {
            'template': self.template.id,
            'data': 'invalid_data'  # Should be dict, not string
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_instance_template_not_found(self):
        """Test creating instance with non-existent template"""
        url = reverse('template-instance-list')
        data = {
            'template': 99999,  # Non-existent ID
            'data': {'EmployeeName': 'Test'}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('templates.services.pdf_service.PDFGenerationService.generate_pdf')
    def test_create_instance_pdf_generation_error(self, mock_pdf):
        """Test handling PDF generation errors"""
        url = reverse('template-instance-list')
        data = {
            'template': self.template.id,
            'data': {'EmployeeName': 'Test'}
        }
        
        # Mock PDF generation to raise an exception
        mock_pdf.side_effect = Exception("PDF generation failed")
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_list_instances(self):
        """Test listing all template instances"""
        url = reverse('template-instance-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['template'], self.template.id)
    
    def test_retrieve_instance(self):
        """Test retrieving a specific template instance"""
        url = reverse('template-instance-detail', kwargs={'pk': self.template_instance.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['template'], self.template.id)
        self.assertEqual(response.data['data'], {"EmployeeName": "John Doe", "SSN": "123-45-6789"})
    
    def test_retrieve_instance_with_file_url(self):
        """Test retrieving instance with file URL when paid"""
        # Set instance as paid and add file
        self.template_instance.is_paid = True
        self.template_instance.file.save('test.pdf', ContentFile(b'test content'))
        self.template_instance.save()
        
        url = reverse('template-instance-detail', kwargs={'pk': self.template_instance.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('file_url', response.data)
        self.assertIsNotNone(response.data['file_url'])
    
    @patch('templates.services.email_service.EmailService.send_download_link_email')
    def test_send_email_success(self, mock_email):
        """Test sending email successfully"""
        # Set instance as paid
        self.template_instance.is_paid = True
        self.template_instance.save()
        
        url = reverse('template-instance-send-email', kwargs={'pk': self.template_instance.id})
        data = {'email': 'test@example.com'}
        
        # Mock email service
        mock_email.return_value = True
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        
        # Verify email service was called
        mock_email.assert_called_once_with(self.template_instance, 'test@example.com')
    
    def test_send_email_not_paid(self):
        """Test sending email when payment not completed"""
        url = reverse('template-instance-send-email', kwargs={'pk': self.template_instance.id})
        data = {'email': 'test@example.com'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
        self.assertIn('Payment not completed', response.data['error'])
    
    def test_send_email_invalid_email(self):
        """Test sending email with invalid email format"""
        # Set instance as paid
        self.template_instance.is_paid = True
        self.template_instance.save()
        
        url = reverse('template-instance-send-email', kwargs={'pk': self.template_instance.id})
        data = {'email': 'invalid-email'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_download_not_paid(self):
        """Test downloading when payment not completed"""
        url = reverse('template-instance-download', kwargs={'pk': self.template_instance.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
        self.assertIn('Payment not completed', response.data['error'])
    
    def test_download_no_file(self):
        """Test downloading when file is missing"""
        # Set instance as paid but no file
        self.template_instance.is_paid = True
        self.template_instance.save()
        
        url = reverse('template-instance-download', kwargs={'pk': self.template_instance.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertIn('PDF file not found', response.data['error'])
    
    def test_download_success(self):
        """Test downloading successfully"""
        # Set instance as paid and add file
        self.template_instance.is_paid = True
        self.template_instance.file.save('test.pdf', ContentFile(b'test content'))
        self.template_instance.save()
        
        url = reverse('template-instance-download', kwargs={'pk': self.template_instance.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('download_url', response.data)
        self.assertIsNotNone(response.data['download_url'])


class APIViewIntegrationTestCase(TestCase):
    """Integration tests for API views with real PDF generation"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Integration Test Template",
            description="Template for integration testing"
        )
        
        # Create a test PDF file for the template
        pdf_content = create_test_pdf_content()
        self.template.file.save('integration_test.pdf', ContentFile(pdf_content))
    
    @patch('templates.services.pdf_service.PDFGenerationService.generate_pdf')
    @patch('templates.services.pdf_service.default_storage')
    @patch('templates.services.stripe_service.StripeService.create_checkout_session')
    def test_full_instance_creation_flow(self, mock_stripe, mock_storage, mock_pdf):
        """Test complete instance creation flow with real PDF generation"""
        url = reverse('template-instance-list')
        data = {
            'template': self.template.id,
            'data': {
                'EmployeeName': 'Integration Test',
                'SSN': '111-22-3333'
            }
        }
        
        # Mock storage
        mock_storage.save.return_value = "templates-instances/test-uuid.pdf"
        
        # Mock PDF generation
        mock_pdf.return_value = 'https://fake-s3-url/test.pdf'
        
        # Mock Stripe checkout session
        mock_stripe.return_value = {
            'session_id': 'cs_test_integration_123',
            'checkout_url': 'https://checkout.stripe.com/pay/cs_test_integration_123'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debug output
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify instance was created
        self.assertEqual(TemplateInstance.objects.count(), 1)
        instance = TemplateInstance.objects.first()
        self.assertEqual(instance.template, self.template)
        self.assertEqual(instance.data, data['data'])
        
        # Verify PDF generation was attempted
        mock_pdf.assert_called_once()
        
        # Verify Stripe checkout was created
        mock_stripe.assert_called_once() 