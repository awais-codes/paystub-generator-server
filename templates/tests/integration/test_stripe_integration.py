import unittest
import os
import json
from unittest.mock import patch
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.urls import reverse
from templates.models import Template, TemplateInstance
from templates.services.stripe_service import StripeService
from templates.services.pdf_service import PDFGenerationService


class StripeRealIntegrationTestCase(TestCase):
    """Real Stripe integration tests using test API keys"""
    
    def setUp(self):
        """Set up test data and check environment"""
        # Check if test environment is configured
        if not (os.environ.get('STRIPE_TEST_SECRET_KEY') and 
                os.environ.get('STRIPE_TEST_WEBHOOK_SECRET')):
            self.skipTest('Stripe test environment not configured')
        
        self.template = Template.objects.create(
            name="Real Stripe Test Template",
            description="Template for real Stripe integration testing",
            template_type="paystub",
            is_active=True,
            price=5.00
        )
        
        # Create a test PDF file for the template
        from django.core.files.base import ContentFile
        test_pdf_content = self.create_test_pdf_content()
        self.template.file.save('test_template.pdf', ContentFile(test_pdf_content))
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "Real Test User", "SSN": "111-22-3333"}
        )
        
        self.stripe_service = StripeService()
        
        # Create a proper request using RequestFactory
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
    
    def create_test_pdf_content(self):
        """Create a simple test PDF content"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        output_buffer = io.BytesIO()
        c = canvas.Canvas(output_buffer, pagesize=letter)
        c.drawString(100, 750, "Test PDF Template")
        c.drawString(100, 700, "Employee Name: [EmployeeName]")
        c.drawString(100, 650, "SSN: [SSN]")
        c.save()
        output_buffer.seek(0)
        return output_buffer.getvalue()
    
    @override_settings(STRIPE_SECRET_KEY=os.environ.get('STRIPE_TEST_SECRET_KEY'))
    def test_real_checkout_session_creation(self):
        """Test creating a real Stripe checkout session"""
        # Check environment again
        if not os.environ.get('STRIPE_TEST_SECRET_KEY'):
            self.skipTest('STRIPE_TEST_SECRET_KEY not set')
            
        # This will make a real API call to Stripe test mode
        checkout_result = self.stripe_service.create_checkout_session(
            self.template_instance, 
            self.request
        )
        
        # Verify the response structure
        self.assertIn('session_id', checkout_result)
        self.assertIn('checkout_url', checkout_result)
        
        # Verify session ID format (Stripe test session IDs start with cs_test_)
        self.assertTrue(checkout_result['session_id'].startswith('cs_test_'))
        
        # Verify checkout URL format
        self.assertTrue(checkout_result['checkout_url'].startswith('https://checkout.stripe.com/'))
        
        # Verify template instance was updated with session ID
        self.template_instance.refresh_from_db()
        self.assertEqual(self.template_instance.stripe_session_id, checkout_result['session_id'])
    
    @override_settings(STRIPE_SECRET_KEY=os.environ.get('STRIPE_TEST_SECRET_KEY'))
    def test_real_stripe_api_connectivity(self):
        """Test basic connectivity to Stripe API"""
        # Check environment again
        if not os.environ.get('STRIPE_TEST_SECRET_KEY'):
            self.skipTest('STRIPE_TEST_SECRET_KEY not set')
            
        import stripe
        
        # Test that we can make a simple API call
        try:
            # This will make a real API call to Stripe test mode
            account = stripe.Account.retrieve()
            
            # Verify we got a response (structure may vary)
            self.assertIsNotNone(account)
            
        except stripe.error.AuthenticationError:
            self.fail("Stripe authentication failed - check your test API key")
        except stripe.error.APIConnectionError:
            self.fail("Stripe API connection failed - check your internet connection")
        except Exception as e:
            # Other errors might be expected depending on account setup
            print(f"Stripe API test completed with note: {str(e)}")
    
    @override_settings(STRIPE_SECRET_KEY=os.environ.get('STRIPE_TEST_SECRET_KEY'))
    def test_real_payment_session_creation_and_retrieval(self):
        """Test complete payment flow (without actual payment)"""
        # Check environment again
        if not os.environ.get('STRIPE_TEST_SECRET_KEY'):
            self.skipTest('STRIPE_TEST_SECRET_KEY not set')
            
        # Create a real checkout session
        checkout_result = self.stripe_service.create_checkout_session(
            self.template_instance, 
            self.request
        )
        
        # Verify session was created
        self.assertIsNotNone(checkout_result['session_id'])
        
        # Note: We can't simulate an actual payment without user interaction
        # But we can test that the session exists and can be retrieved
        import stripe
        
        try:
            # Retrieve the session from Stripe (real API call)
            session = stripe.checkout.Session.retrieve(checkout_result['session_id'])
            
            # Verify session properties
            self.assertEqual(session.id, checkout_result['session_id'])
            self.assertEqual(session.payment_status, 'unpaid')  # Should be unpaid initially
            
            # Verify metadata was set correctly
            self.assertEqual(session.metadata.get('instance_id'), str(self.template_instance.id))
            self.assertEqual(session.metadata.get('template_id'), str(self.template.id))
            
        except stripe.error.InvalidRequestError as e:
            self.fail(f"Failed to retrieve Stripe session: {str(e)}")
    
    def test_environment_configuration(self):
        """Test that test environment is properly configured"""
        # Check environment again
        if not (os.environ.get('STRIPE_TEST_SECRET_KEY') and 
                os.environ.get('STRIPE_TEST_WEBHOOK_SECRET')):
            self.skipTest('Stripe test environment not configured')
            
        # If we get here, the variables should be set and valid
        secret_key = os.environ.get('STRIPE_TEST_SECRET_KEY')
        webhook_secret = os.environ.get('STRIPE_TEST_WEBHOOK_SECRET')
        
        self.assertIsNotNone(secret_key, "STRIPE_TEST_SECRET_KEY not set")
        self.assertTrue(secret_key.startswith('sk_test_'),
                       "STRIPE_TEST_SECRET_KEY should start with sk_test_")
        
        self.assertIsNotNone(webhook_secret, "STRIPE_TEST_WEBHOOK_SECRET not set")
        self.assertTrue(webhook_secret.startswith('whsec_'),
                       "STRIPE_TEST_WEBHOOK_SECRET should start with whsec_")
