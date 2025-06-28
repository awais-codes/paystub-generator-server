import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.http import HttpRequest
from django.urls import reverse
from django.test.client import RequestFactory
import os
import unittest

from .models import Template, TemplateInstance
from .services.stripe_service import StripeService


@unittest.skipUnless(os.environ.get('STRIPE_SECRET_KEY'), 'Stripe environment not set')
class StripeServiceTestCase(TestCase):
    """Test cases for StripeService"""
    
    def setUp(self):
        """Set up test data"""
        self.template = Template.objects.create(
            name="Test Paystub Template",
            description="A test template for paystub generation"
        )
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "John Doe", "SSN": "123-45-6789"}
        )
        
        self.stripe_service = StripeService()
        
        # Create a proper request using RequestFactory
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
    
    @patch('templates.services.stripe_service.stripe')
    def test_create_checkout_session(self, mock_stripe):
        """Test creating a Stripe checkout session"""
        # Mock Stripe session creation
        mock_session = MagicMock()
        mock_session.id = 'cs_test_123456789'
        mock_session.url = 'https://checkout.stripe.com/pay/cs_test_123456789'
        mock_stripe.checkout.Session.create.return_value = mock_session
        
        # Test creating checkout session
        result = self.stripe_service.create_checkout_session(
            self.template_instance, 
            self.request
        )
        
        # Verify Stripe was called with correct parameters
        mock_stripe.checkout.Session.create.assert_called_once()
        call_args = mock_stripe.checkout.Session.create.call_args
        
        # Verify payment method types
        self.assertIn('card', call_args[1]['payment_method_types'])
        
        # Verify line items
        line_items = call_args[1]['line_items']
        self.assertEqual(len(line_items), 1)
        self.assertEqual(line_items[0]['quantity'], 1)
        
        # Verify price data
        price_data = line_items[0]['price_data']
        self.assertEqual(price_data['currency'], 'usd')
        self.assertEqual(price_data['unit_amount'], 500)  # $5.00
        
        # Verify product data
        product_data = price_data['product_data']
        self.assertIn('PDF Document', product_data['name'])
        self.assertIn(self.template.name, product_data['name'])
        
        # Verify metadata
        metadata = call_args[1]['metadata']
        self.assertEqual(metadata['instance_id'], str(self.template_instance.id))
        self.assertEqual(metadata['template_id'], str(self.template.id))
        
        # Verify result
        self.assertEqual(result['session_id'], 'cs_test_123456789')
        self.assertEqual(result['checkout_url'], 'https://checkout.stripe.com/pay/cs_test_123456789')
        
        # Verify template instance was updated
        self.template_instance.refresh_from_db()
        self.assertEqual(self.template_instance.stripe_session_id, 'cs_test_123456789')
    
    @patch('templates.services.stripe_service.stripe')
    def test_create_checkout_session_error(self, mock_stripe):
        """Test handling errors when creating checkout session"""
        # Mock Stripe to raise an exception
        mock_stripe.checkout.Session.create.side_effect = Exception("Stripe API error")
        
        with self.assertRaises(Exception) as context:
            self.stripe_service.create_checkout_session(
                self.template_instance, 
                self.request
            )
        
        self.assertIn("Error creating Stripe checkout session", str(context.exception))
    
    @patch('templates.services.stripe_service.stripe')
    def test_verify_webhook_signature_valid(self, mock_stripe):
        """Test verifying valid webhook signature"""
        # Mock webhook payload and signature
        payload = b'{"type": "checkout.session.completed", "data": {"object": {"id": "cs_test_123"}}}'
        sig_header = 't=1234567890,v1=abc123'
        webhook_secret = 'whsec_test_secret'
        
        # Mock Stripe webhook verification
        mock_event = {
            'type': 'checkout.session.completed',
            'data': {'object': {'id': 'cs_test_123'}}
        }
        mock_stripe.Webhook.construct_event.return_value = mock_event
        
        # Test verification
        result = self.stripe_service.verify_webhook_signature(
            payload, sig_header, webhook_secret
        )
        
        # Verify Stripe was called correctly
        mock_stripe.Webhook.construct_event.assert_called_once_with(
            payload, sig_header, webhook_secret
        )
        
        # Verify result
        self.assertEqual(result, mock_event)
    
    @patch('templates.services.stripe_service.stripe')
    def test_verify_webhook_signature_invalid_payload(self, mock_stripe):
        """Test handling invalid webhook payload"""
        payload = b'invalid payload'
        sig_header = 't=1234567890,v1=abc123'
        webhook_secret = 'whsec_test_secret'
        
        # Mock Stripe to raise ValueError for invalid payload
        mock_stripe.Webhook.construct_event.side_effect = ValueError("Invalid payload")
        
        with self.assertRaises(ValueError) as context:
            self.stripe_service.verify_webhook_signature(
                payload, sig_header, webhook_secret
            )
        
        self.assertEqual(str(context.exception), "Invalid payload")
    
    @patch('templates.services.stripe_service.stripe')
    def test_verify_webhook_signature_invalid_signature(self, mock_stripe):
        """Test handling invalid webhook signature"""
        payload = b'{"type": "checkout.session.completed"}'
        sig_header = 't=1234567890,v1=invalid'
        webhook_secret = 'whsec_test_secret'
        
        # Mock Stripe to raise SignatureVerificationError
        from stripe.error import SignatureVerificationError
        mock_stripe.Webhook.construct_event.side_effect = SignatureVerificationError(
            "Invalid signature", sig_header
        )
        
        with self.assertRaises(ValueError) as context:
            self.stripe_service.verify_webhook_signature(
                payload, sig_header, webhook_secret
            )
        
        self.assertEqual(str(context.exception), "Invalid signature")
    
    @patch('templates.services.stripe_service.stripe')
    def test_handle_payment_success(self, mock_stripe):
        """Test handling successful payment"""
        session_id = 'cs_test_123456789'
        
        # Set up template instance with session ID
        self.template_instance.stripe_session_id = session_id
        self.template_instance.save()
        
        # Mock Stripe session retrieval
        mock_session = MagicMock()
        mock_session.payment_status = 'paid'
        mock_stripe.checkout.Session.retrieve.return_value = mock_session
        
        # Test payment success handling
        result = self.stripe_service.handle_payment_success(session_id)
        
        # Verify Stripe was called
        mock_stripe.checkout.Session.retrieve.assert_called_once_with(session_id)
        
        # Verify template instance was updated
        self.template_instance.refresh_from_db()
        self.assertTrue(self.template_instance.is_paid)
        
        # Verify result
        self.assertEqual(result, self.template_instance)
    
    @patch('templates.services.stripe_service.stripe')
    def test_handle_payment_success_unpaid(self, mock_stripe):
        """Test handling unpaid session"""
        session_id = 'cs_test_123456789'
        
        # Set up template instance with session ID
        self.template_instance.stripe_session_id = session_id
        self.template_instance.save()
        
        # Mock Stripe session retrieval with unpaid status
        mock_session = MagicMock()
        mock_session.payment_status = 'unpaid'
        mock_stripe.checkout.Session.retrieve.return_value = mock_session
        
        # Test payment success handling
        with self.assertRaises(Exception) as context:
            self.stripe_service.handle_payment_success(session_id)
        
        self.assertEqual(str(context.exception), "Payment not completed")
        
        # Verify template instance was not updated
        self.template_instance.refresh_from_db()
        self.assertFalse(self.template_instance.is_paid)
    
    def test_handle_payment_success_instance_not_found(self):
        """Test handling payment success for non-existent instance"""
        session_id = 'cs_test_nonexistent'
        
        with self.assertRaises(Exception) as context:
            self.stripe_service.handle_payment_success(session_id)
        
        self.assertEqual(str(context.exception), "Template instance not found")
    
    @patch('templates.services.stripe_service.stripe')
    def test_handle_payment_success_stripe_error(self, mock_stripe):
        """Test handling Stripe errors during payment success"""
        session_id = 'cs_test_123456789'
        
        # Set up template instance with session ID
        self.template_instance.stripe_session_id = session_id
        self.template_instance.save()
        
        # Mock Stripe to raise an exception
        mock_stripe.checkout.Session.retrieve.side_effect = Exception("Stripe API error")
        
        with self.assertRaises(Exception) as context:
            self.stripe_service.handle_payment_success(session_id)
        
        self.assertIn("Error handling payment success", str(context.exception))


@unittest.skipUnless(os.environ.get('STRIPE_SECRET_KEY'), 'Stripe environment not set')
class StripeServiceIntegrationTestCase(TestCase):
    """Integration tests for Stripe service with real Stripe API calls (if configured)"""
    
    def setUp(self):
        """Set up test data"""
        self.template = Template.objects.create(
            name="Integration Test Template",
            description="Template for integration testing"
        )
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "Jane Smith", "SSN": "987-65-4321"}
        )
        
        self.stripe_service = StripeService()
        
        # Create a proper request using RequestFactory
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
    
    @override_settings(STRIPE_SECRET_KEY='sk_test_dummy_key')
    @patch('templates.services.stripe_service.stripe')
    def test_full_payment_flow(self, mock_stripe):
        """Test complete payment flow from checkout to success"""
        # Mock checkout session creation
        mock_session = MagicMock()
        mock_session.id = 'cs_test_integration_123'
        mock_session.url = 'https://checkout.stripe.com/pay/cs_test_integration_123'
        mock_stripe.checkout.Session.create.return_value = mock_session
        
        # Create checkout session
        checkout_result = self.stripe_service.create_checkout_session(
            self.template_instance, 
            self.request
        )
        
        self.assertEqual(checkout_result['session_id'], 'cs_test_integration_123')
        
        # Mock session retrieval for payment success
        mock_session.payment_status = 'paid'
        mock_stripe.checkout.Session.retrieve.return_value = mock_session
        
        # Handle payment success
        result = self.stripe_service.handle_payment_success('cs_test_integration_123')
        
        # Verify the complete flow worked
        self.template_instance.refresh_from_db()
        self.assertTrue(self.template_instance.is_paid)
        self.assertEqual(result, self.template_instance) 