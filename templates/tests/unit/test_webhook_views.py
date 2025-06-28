import json
import uuid
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.base import ContentFile
from rest_framework.test import APIClient
from rest_framework import status

from templates.models import Template, TemplateInstance
from templates.services.stripe_service import StripeService
from .test_utils import create_test_pdf_content


class StripeWebhookViewTestCase(TestCase):
    """Test cases for StripeWebhookView"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Webhook Test Template",
            description="Template for webhook testing"
        )
        
        # Create a test PDF file for the template
        pdf_content = create_test_pdf_content()
        self.template.file.save('webhook_test.pdf', ContentFile(pdf_content))
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "Webhook Test", "SSN": "999-88-7777"},
            stripe_session_id='cs_test_webhook_123'
        )
    
    @patch('templates.views.webhook.StripeService')
    def test_webhook_checkout_session_completed(self, mock_stripe_service_class):
        """Test handling checkout.session.completed webhook"""
        url = reverse('stripe-webhook')
        
        # Mock webhook payload
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_webhook_123',
                    'payment_status': 'paid',
                    'metadata': {
                        'instance_id': str(self.template_instance.id),
                        'template_id': str(self.template.id)
                    }
                }
            }
        }
        
        # Mock StripeService instance
        mock_stripe_service = MagicMock()
        mock_stripe_service_class.return_value = mock_stripe_service
        
        # Mock webhook verification
        mock_stripe_service.verify_webhook_signature.return_value = webhook_payload
        
        # Mock payment success handling
        mock_stripe_service.handle_payment_success.return_value = self.template_instance
        
        # Send webhook request
        response = self.client.post(
            url,
            data=json.dumps(webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=abc123'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify webhook was verified
        mock_stripe_service.verify_webhook_signature.assert_called_once()
        
        # Verify payment was handled
        mock_stripe_service.handle_payment_success.assert_called_once_with('cs_test_webhook_123')
        
        # Verify response is JSON
        response_data = json.loads(response.content)
        self.assertIn('status', response_data)
        self.assertEqual(response_data['status'], 'Payment processed successfully')
    
    @patch('templates.views.webhook.StripeService')
    def test_webhook_other_event_types(self, mock_stripe_service_class):
        """Test handling other webhook event types"""
        url = reverse('stripe-webhook')
        
        # Mock webhook payload for different event type
        webhook_payload = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123'
                }
            }
        }
        
        # Mock StripeService instance
        mock_stripe_service = MagicMock()
        mock_stripe_service_class.return_value = mock_stripe_service
        
        # Mock webhook verification
        mock_stripe_service.verify_webhook_signature.return_value = webhook_payload
        
        # Send webhook request
        response = self.client.post(
            url,
            data=json.dumps(webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=abc123'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify webhook was verified but no payment handling
        mock_stripe_service.verify_webhook_signature.assert_called_once()
        
        # Verify response is JSON
        response_data = json.loads(response.content)
        self.assertIn('status', response_data)
        self.assertEqual(response_data['status'], 'Event ignored')
    
    @patch('templates.views.webhook.StripeService')
    def test_webhook_invalid_signature(self, mock_stripe_service_class):
        """Test handling webhook with invalid signature"""
        url = reverse('stripe-webhook')
        
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {'object': {'id': 'cs_test_123'}}
        }
        
        # Mock StripeService instance
        mock_stripe_service = MagicMock()
        mock_stripe_service_class.return_value = mock_stripe_service
        
        # Mock webhook verification to raise ValueError
        mock_stripe_service.verify_webhook_signature.side_effect = ValueError("Invalid signature")
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=invalid'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Invalid signature', response_data['error'])
    
    @patch('templates.views.webhook.StripeService')
    def test_webhook_invalid_payload(self, mock_stripe_service_class):
        """Test handling webhook with invalid payload"""
        url = reverse('stripe-webhook')
        
        # Mock StripeService instance
        mock_stripe_service = MagicMock()
        mock_stripe_service_class.return_value = mock_stripe_service
        
        # Mock webhook verification to raise ValueError for invalid payload
        mock_stripe_service.verify_webhook_signature.side_effect = ValueError("Invalid payload")
        
        response = self.client.post(
            url,
            data='invalid json',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=abc123'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Invalid JSON', response_data['error'])
    
    @patch('templates.views.webhook.StripeService')
    def test_webhook_payment_handling_error(self, mock_stripe_service_class):
        """Test handling errors during payment processing"""
        url = reverse('stripe-webhook')
        
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_webhook_123',
                    'payment_status': 'paid'
                }
            }
        }
        
        # Mock StripeService instance
        mock_stripe_service = MagicMock()
        mock_stripe_service_class.return_value = mock_stripe_service
        
        # Mock webhook verification
        mock_stripe_service.verify_webhook_signature.return_value = webhook_payload
        
        # Mock payment handling to raise an exception
        mock_stripe_service.handle_payment_success.side_effect = Exception("Payment processing failed")
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=abc123'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Error processing webhook', response_data['error'])
    
    def test_webhook_missing_signature_header(self):
        """Test handling webhook without signature header"""
        url = reverse('stripe-webhook')
        
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {'object': {'id': 'cs_test_123'}}
        }
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_payload),
            content_type='application/json'
            # No HTTP_STRIPE_SIGNATURE header
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Missing Stripe signature', response_data['error'])
    
    def test_webhook_invalid_json(self):
        """Test handling webhook with invalid JSON"""
        url = reverse('stripe-webhook')
        
        response = self.client.post(
            url,
            data='invalid json data',
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=abc123'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Invalid JSON', response_data['error'])
    
    @patch('templates.views.webhook.StripeService')
    def test_webhook_instance_not_found(self, mock_stripe_service_class):
        """Test handling webhook for non-existent instance"""
        url = reverse('stripe-webhook')
        
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_nonexistent',
                    'payment_status': 'paid'
                }
            }
        }
        
        # Mock StripeService instance
        mock_stripe_service = MagicMock()
        mock_stripe_service_class.return_value = mock_stripe_service
        
        # Mock webhook verification
        mock_stripe_service.verify_webhook_signature.return_value = webhook_payload
        
        # Mock payment handling to raise exception for non-existent instance
        mock_stripe_service.handle_payment_success.side_effect = Exception("Template instance not found")
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=abc123'
        )
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Error processing webhook', response_data['error'])


class WebhookViewIntegrationTestCase(TestCase):
    """Integration tests for webhook views with database interactions"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Integration Webhook Template",
            description="Template for webhook integration testing"
        )
        
        # Create a test PDF file for the template
        pdf_content = create_test_pdf_content()
        self.template.file.save('integration_webhook.pdf', ContentFile(pdf_content))
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "Integration Test", "SSN": "111-22-3333"},
            stripe_session_id='cs_test_integration_webhook_123'
        )
    
    @patch('templates.views.webhook.StripeService')
    def test_webhook_database_interaction(self, mock_stripe_service_class):
        """Test webhook processing with database interaction"""
        url = reverse('stripe-webhook')
        
        # Mock webhook payload
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_integration_webhook_123',
                    'payment_status': 'paid',
                    'metadata': {
                        'instance_id': str(self.template_instance.id),
                        'template_id': str(self.template.id)
                    }
                }
            }
        }
        
        # Mock StripeService instance
        mock_stripe_service = MagicMock()
        mock_stripe_service_class.return_value = mock_stripe_service
        
        # Mock webhook verification
        mock_stripe_service.verify_webhook_signature.return_value = webhook_payload
        
        # Mock payment success handling to actually update the database
        def mock_handle_payment_success(session_id):
            # Actually update the template instance in the database
            instance = TemplateInstance.objects.get(stripe_session_id=session_id)
            instance.is_paid = True
            instance.save()
            return instance
        
        mock_stripe_service.handle_payment_success.side_effect = mock_handle_payment_success
        
        # Send webhook request
        response = self.client.post(
            url,
            data=json.dumps(webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=abc123'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify template instance was updated in database
        self.template_instance.refresh_from_db()
        self.assertTrue(self.template_instance.is_paid)
        
        # Verify Stripe service was called correctly
        mock_stripe_service.verify_webhook_signature.assert_called_once()
        mock_stripe_service.handle_payment_success.assert_called_once_with('cs_test_integration_webhook_123')
    
    @override_settings(STRIPE_WEBHOOK_SECRET='whsec_test_secret')
    @patch('templates.views.webhook.StripeService')
    def test_webhook_with_environment_secret(self, mock_stripe_service_class):
        """Test webhook processing with environment webhook secret"""
        url = reverse('stripe-webhook')
        
        webhook_payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                    'payment_status': 'paid'
                }
            }
        }
        
        # Mock StripeService instance
        mock_stripe_service = MagicMock()
        mock_stripe_service_class.return_value = mock_stripe_service
        
        # Mock the webhook_secret attribute
        mock_stripe_service.webhook_secret = 'whsec_test_secret'
        
        # Mock webhook verification
        mock_stripe_service.verify_webhook_signature.return_value = webhook_payload
        
        response = self.client.post(
            url,
            data=json.dumps(webhook_payload),
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE='t=1234567890,v1=abc123'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify webhook secret was used
        mock_stripe_service.verify_webhook_signature.assert_called_once()
        call_args = mock_stripe_service.verify_webhook_signature.call_args
        self.assertEqual(call_args[0][2], 'whsec_test_secret')  # webhook_secret parameter 