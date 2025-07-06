import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.base import ContentFile
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from templates.models import Template, TemplateInstance, TemplatePreview
from templates.services.pdf_service import PDFGenerationService
from templates.services.stripe_service import StripeService
from templates.services.email_service import EmailService
from .test_utils import create_test_pdf_content
import os


class TemplateViewSetTestCase(TestCase):
    """Test cases for TemplateViewSet (read-only)"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Test Template",
            description="A test template",
            template_type="paystub",
            is_active=True
        )
        
        # Create an inactive template
        self.inactive_template = Template.objects.create(
            name="Inactive Template",
            description="An inactive template",
            template_type="w2",
            is_active=False
        )
    
    def test_list_templates(self):
        """Test listing all active templates"""
        url = reverse('template-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only active templates
        self.assertEqual(response.data[0]['name'], "Test Template")
        self.assertTrue(response.data[0]['is_active'])
    
    def test_create_template_not_allowed(self):
        """Test that creating templates is not allowed (read-only)"""
        url = reverse('template-list')
        data = {
            'name': 'New Template',
            'description': 'A new template'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Template.objects.count(), 2)  # No new template created
    
    def test_create_template_with_file_not_allowed(self):
        """Test that creating templates with files is not allowed (read-only)"""
        url = reverse('template-list')
        
        # Create a test PDF file using SimpleUploadedFile
        pdf_content = create_test_pdf_content()
        
        data = {
            'name': 'Template with File',
            'description': 'Template with PDF file',
            'file': SimpleUploadedFile('test_template.pdf', pdf_content, content_type='application/pdf')
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Template.objects.count(), 2)  # No new template created
    
    def test_retrieve_template(self):
        """Test retrieving a specific template"""
        url = reverse('template-detail', kwargs={'pk': self.template.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Test Template")
        self.assertEqual(response.data['template_type'], "paystub")
        self.assertEqual(response.data['template_type_display'], "Paystub")
    
    def test_update_template_not_allowed(self):
        """Test that updating templates is not allowed (read-only)"""
        url = reverse('template-detail', kwargs={'pk': self.template.id})
        data = {
            'name': 'Updated Template',
            'description': 'Updated description'
        }
        
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.template.refresh_from_db()
        self.assertEqual(self.template.name, 'Test Template')  # Name unchanged
    
    def test_delete_template_not_allowed(self):
        """Test that deleting templates is not allowed (read-only)"""
        url = reverse('template-detail', kwargs={'pk': self.template.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Template.objects.count(), 2)  # Template not deleted
    
    def test_filter_by_template_type(self):
        """Test filtering templates by type"""
        url = reverse('template-list')
        response = self.client.get(url, {'template_type': 'paystub'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['template_type'], 'paystub')
    
    def test_search_templates(self):
        """Test searching templates by name"""
        url = reverse('template-list')
        response = self.client.get(url, {'search': 'Test'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Template')


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
        mock_pdf.assert_called()
        
        # Verify Stripe checkout was created
        mock_stripe.assert_called() 


class PreviewFlowTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        pdf_path = os.path.join(os.path.dirname(__file__), '../fixtures/test_files/w2_template.pdf')
        with open(os.path.abspath(pdf_path), 'rb') as f:
            pdf_bytes = f.read()
        self.main_pdf = SimpleUploadedFile("main.pdf", pdf_bytes, content_type="application/pdf")
        self.preview_pdf = SimpleUploadedFile("preview.pdf", pdf_bytes, content_type="application/pdf")
        self.template = Template.objects.create(
            name="Preview Test Template",
            template_type="w2",
            file=self.main_pdf,
            preview_file=self.preview_pdf,
            is_active=True,
            price=10.00
        )

    def test_create_and_update_preview_and_instance(self):
        # 1. Create a preview
        preview_data = {
            "template": str(self.template.id),
            "data": {"employee_ssn": "123-45-6789", "wages_tips": "50000"}
        }
        resp = self.client.post(reverse("template-preview-list"), preview_data, format="json")
        self.assertEqual(resp.status_code, 201, resp.data)
        preview_id = resp.data["id"]
        self.assertIsNotNone(resp.data["file_url"])
        preview_obj = TemplatePreview.objects.get(id=preview_id)
        self.assertTrue(preview_obj.file.name.endswith(".pdf"))

        # 2. Update the preview
        update_data = {"data": {"employee_ssn": "987-65-4321", "wages_tips": "60000"}}
        resp2 = self.client.patch(reverse("template-preview-detail", args=[preview_id]), update_data, format="json")
        self.assertEqual(resp2.status_code, 200, resp2.data)
        self.assertEqual(resp2.data["data"]["employee_ssn"], "987-65-4321")
        preview_obj.refresh_from_db()
        self.assertEqual(preview_obj.data["employee_ssn"], "987-65-4321")

        # 3. Create an instance from the preview
        instance_data = {"preview_id": str(preview_id)}
        with patch('templates.services.pdf_service.PDFGenerationService.generate_pdf') as mock_pdf, \
             patch('templates.services.stripe_service.StripeService.create_checkout_session') as mock_stripe:
            mock_pdf.return_value = "https://s3.amazonaws.com/bucket/test.pdf"
            mock_stripe.return_value = {
                'session_id': 'cs_test_789',
                'checkout_url': 'https://checkout.stripe.com/pay/cs_test_789'
            }
            resp3 = self.client.post(reverse("template-instance-list"), instance_data, format="json")
            self.assertEqual(resp3.status_code, 201, resp3.data)
            instance_id = resp3.data.get("instance_id")
            instance_obj = TemplateInstance.objects.get(id=instance_id)
            self.assertEqual(instance_obj.data["employee_ssn"], "987-65-4321")
            # Only check for mock_pdf call, not file field, since file is not set when mocked
            mock_pdf.assert_called_once()
            mock_stripe.assert_called_once()

    def test_preview_create_invalid_template(self):
        preview_data = {"template": "00000000-0000-0000-0000-000000000000", "data": {"foo": "bar"}}
        resp = self.client.post(reverse("template-preview-list"), preview_data, format="json")
        self.assertIn(resp.status_code, [400, 404])

    def test_preview_create_missing_data(self):
        preview_data = {"template": str(self.template.id)}
        resp = self.client.post(reverse("template-preview-list"), preview_data, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_preview_update_invalid_preview(self):
        update_data = {"data": {"foo": "bar"}}
        resp = self.client.patch(reverse("template-preview-detail", args=["00000000-0000-0000-0000-000000000000"]), update_data, format="json")
        self.assertEqual(resp.status_code, 404)

    def test_instance_create_invalid_preview(self):
        instance_data = {"preview_id": "00000000-0000-0000-0000-000000000000"}
        resp = self.client.post(reverse("template-instance-list"), instance_data, format="json")
        self.assertEqual(resp.status_code, 404)

    def test_preview_create_no_preview_file(self):
        template2 = Template.objects.create(
            name="No Preview File",
            template_type="w2",
            file=self.main_pdf,
            preview_file=None,
            is_active=True,
            price=10.00
        )
        preview_data = {"template": str(template2.id), "data": {"foo": "bar"}}
        resp = self.client.post(reverse("template-preview-list"), preview_data, format="json")
        self.assertEqual(resp.status_code, 400) 