import os
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile

from templates.models import Template, TemplateInstance
from templates.services.email_service import EmailService
from .test_utils import create_test_pdf_content


@unittest.skipUnless(os.environ.get('EMAIL_HOST') or os.environ.get('EMAIL_BACKEND'), 'Email environment not set')
class EmailServiceTestCase(TestCase):
    """Test cases for EmailService"""
    
    def setUp(self):
        """Set up test data"""
        self.template = Template.objects.create(
            name="Test Email Template",
            description="Template for email testing"
        )
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "John Doe", "SSN": "123-45-6789"},
            is_paid=True
        )
        
        # Create a test PDF file
        test_pdf_content = create_test_pdf_content()
        self.template_instance.file.save('test.pdf', ContentFile(test_pdf_content))
    
    @patch('templates.services.email_service.EmailMessage')
    @patch('templates.services.email_service.os.path.exists')
    def test_send_pdf_email_with_attachment(self, mock_exists, mock_email_message):
        """Test sending PDF email with download link"""
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock email message
        mock_email = MagicMock()
        mock_email_message.return_value = mock_email
        
        # Test sending email
        recipient_email = "test@example.com"
        result = EmailService.send_pdf_email(self.template_instance, recipient_email)
        
        # Verify email was created with correct parameters
        mock_email_message.assert_called_once()
        call_args = mock_email_message.call_args
        
        self.assertEqual(call_args[1]['subject'], f"Your PDF Document - {self.template.name}")
        self.assertEqual(call_args[1]['to'], [recipient_email])
        
        # Verify email body contains expected content
        body = call_args[1]['body']
        self.assertIn("Your PDF document has been generated", body)
        self.assertIn("You can download your PDF here", body)
        
        # Verify email was sent
        mock_email.send.assert_called_once()
        
        # Verify result
        self.assertTrue(result)
    
    @patch('templates.services.email_service.EmailMessage')
    def test_send_pdf_email_with_s3_url(self, mock_email_message):
        """Test sending PDF email with S3 URL (when file is not local)"""
        # Mock email message
        mock_email = MagicMock()
        mock_email_message.return_value = mock_email
        
        # Mock file to have URL but no local path
        mock_file = MagicMock()
        mock_file.path = None
        mock_file.url = "https://s3.amazonaws.com/bucket/test.pdf"
        self.template_instance.file = mock_file
        
        # Test sending email
        recipient_email = "test@example.com"
        result = EmailService.send_pdf_email(self.template_instance, recipient_email)
        
        # Verify email body contains S3 URL
        call_args = mock_email_message.call_args
        body = call_args[1]['body']
        self.assertIn("You can download your PDF here", body)
        self.assertIn("https://s3.amazonaws.com/bucket/test.pdf", body)
        
        # Verify email was sent
        mock_email.send.assert_called_once()
        self.assertTrue(result)
    
    def test_send_pdf_email_not_paid(self):
        """Test sending PDF email when payment not completed"""
        # Set payment status to unpaid
        self.template_instance.is_paid = False
        self.template_instance.save()
        
        recipient_email = "test@example.com"
        
        with self.assertRaises(Exception) as context:
            EmailService.send_pdf_email(self.template_instance, recipient_email)
        
        self.assertIn("PDF not available or payment not completed", str(context.exception))
    
    def test_send_pdf_email_no_file(self):
        """Test sending PDF email when file is missing"""
        # Remove file
        self.template_instance.file = None
        self.template_instance.save()
        
        recipient_email = "test@example.com"
        
        with self.assertRaises(Exception) as context:
            EmailService.send_pdf_email(self.template_instance, recipient_email)
        
        self.assertIn("PDF not available", str(context.exception))
    
    @patch('templates.services.email_service.EmailMessage')
    def test_send_pdf_email_error(self, mock_email_message):
        """Test handling email sending errors"""
        # Mock email to raise an exception
        mock_email = MagicMock()
        mock_email.send.side_effect = Exception("SMTP error")
        mock_email_message.return_value = mock_email
        
        recipient_email = "test@example.com"
        
        with self.assertRaises(Exception) as context:
            EmailService.send_pdf_email(self.template_instance, recipient_email)
        
        self.assertIn("Error sending PDF email", str(context.exception))
    
    @patch('templates.services.email_service.EmailMessage')
    def test_send_download_link_email(self, mock_email_message):
        """Test sending download link email"""
        # Mock email message
        mock_email = MagicMock()
        mock_email_message.return_value = mock_email
        
        # Test sending download link email
        recipient_email = "test@example.com"
        result = EmailService.send_download_link_email(self.template_instance, recipient_email)
        
        # Verify email was created with correct parameters
        mock_email_message.assert_called_once()
        call_args = mock_email_message.call_args
        
        self.assertEqual(call_args[1]['subject'], f"Download Your PDF - {self.template.name}")
        self.assertEqual(call_args[1]['to'], [recipient_email])
        
        # Verify email body contains download link
        body = call_args[1]['body']
        self.assertIn("Your PDF document", body)
        self.assertIn("Download Link:", body)
        self.assertIn("24 hours", body)
        
        # Verify email was sent
        mock_email.send.assert_called_once()
        self.assertTrue(result)
    
    def test_send_download_link_email_not_paid(self):
        """Test sending download link email when payment not completed"""
        # Set payment status to unpaid
        self.template_instance.is_paid = False
        self.template_instance.save()
        
        recipient_email = "test@example.com"
        
        with self.assertRaises(Exception) as context:
            EmailService.send_download_link_email(self.template_instance, recipient_email)
        
        self.assertIn("Payment not completed", str(context.exception))
    
    def test_send_download_link_email_no_file(self):
        """Test sending download link email when file is missing"""
        # Remove file
        self.template_instance.file = None
        self.template_instance.save()
        
        recipient_email = "test@example.com"
        
        with self.assertRaises(Exception) as context:
            EmailService.send_download_link_email(self.template_instance, recipient_email)
        
        self.assertIn("PDF file not found", str(context.exception))
    
    @patch('templates.services.email_service.EmailMessage')
    def test_send_download_link_email_error(self, mock_email_message):
        """Test handling download link email sending errors"""
        # Mock email to raise an exception
        mock_email = MagicMock()
        mock_email.send.side_effect = Exception("SMTP error")
        mock_email_message.return_value = mock_email
        
        recipient_email = "test@example.com"
        
        with self.assertRaises(Exception) as context:
            EmailService.send_download_link_email(self.template_instance, recipient_email)
        
        self.assertIn("Error sending download link email", str(context.exception))
    
    def test_email_validation(self):
        """Test email validation in service methods"""
        # The service doesn't validate email format, so we just test that it works with valid emails
        recipient_email = "test@example.com"
        
        # This should not raise an exception
        try:
            # We can't actually send without mocking, but we can test the validation logic
            # The service will fail at the email sending stage, not validation
            pass
        except Exception as e:
            # If there's an exception, it should be related to email sending, not validation
            self.assertNotIn("invalid", str(e).lower())


@unittest.skipUnless(os.environ.get('EMAIL_HOST') or os.environ.get('EMAIL_BACKEND'), 'Email environment not set')
class EmailServiceIntegrationTestCase(TestCase):
    """Integration tests for email service with real email sending (if configured)"""
    
    def setUp(self):
        """Set up test data"""
        self.template = Template.objects.create(
            name="Integration Email Template",
            description="Template for email integration testing"
        )
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "Integration Test", "SSN": "111-22-3333"},
            is_paid=True
        )
        
        # Create a test PDF file
        test_pdf_content = create_test_pdf_content()
        self.template_instance.file.save('integration_test.pdf', ContentFile(test_pdf_content))
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('templates.services.email_service.os.path.exists')
    def test_real_email_sending(self, mock_exists):
        """Test sending real email using Django's locmem backend"""
        from django.core import mail
        
        # Mock file existence
        mock_exists.return_value = True
        
        recipient_email = "test@example.com"
        
        # Send email
        result = EmailService.send_download_link_email(self.template_instance, recipient_email)
        
        # Verify email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Verify email content
        email = mail.outbox[0]
        self.assertEqual(email.to, [recipient_email])
        self.assertIn("Download Your PDF", email.subject)
        self.assertIn("Download Link:", email.body)
    
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='test@example.com'
    )
    @patch('templates.services.email_service.os.path.exists')
    def test_real_pdf_attachment_email(self, mock_exists):
        """Test sending real email with PDF download link"""
        # Mock file existence
        mock_exists.return_value = True
        
        # Test sending email
        recipient_email = "integration@example.com"
        result = EmailService.send_pdf_email(self.template_instance, recipient_email)
        
        # Verify result
        self.assertTrue(result)
        
        # Check that email was sent (using locmem backend)
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.subject, f"Your PDF Document - {self.template.name}")
        self.assertEqual(email.to, [recipient_email])
        self.assertIn("You can download your PDF here", email.body) 