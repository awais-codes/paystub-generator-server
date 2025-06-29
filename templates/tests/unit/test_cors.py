from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from templates.models import Template


class CORSTestCase(TestCase):
    """Test cases for CORS configuration"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.template = Template.objects.create(
            name="Test Template",
            description="A test template",
            template_type="paystub",
            is_active=True
        )
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in API responses"""
        url = reverse('template-list')
        
        # Test with a common React development origin
        response = self.client.get(
            url,
            HTTP_ORIGIN='http://localhost:3000'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that CORS headers are present
        self.assertIn('Access-Control-Allow-Origin', response)
        self.assertEqual(
            response['Access-Control-Allow-Origin'],
            'http://localhost:3000'
        )
    
    def test_cors_preflight_request(self):
        """Test CORS preflight OPTIONS request"""
        url = reverse('template-list')
        
        response = self.client.options(
            url,
            HTTP_ORIGIN='http://localhost:3000',
            HTTP_ACCESS_CONTROL_REQUEST_METHOD='POST',
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS='content-type'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check CORS headers for preflight
        self.assertIn('Access-Control-Allow-Origin', response)
        self.assertIn('Access-Control-Allow-Methods', response)
        self.assertIn('Access-Control-Allow-Headers', response)
    
    def test_cors_credentials_allowed(self):
        """Test that credentials are allowed in CORS requests"""
        url = reverse('template-list')
        
        response = self.client.get(
            url,
            HTTP_ORIGIN='http://localhost:3000'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that credentials are allowed
        self.assertIn('Access-Control-Allow-Credentials', response)
        self.assertEqual(
            response['Access-Control-Allow-Credentials'],
            'true'
        )
    
    def test_cors_multiple_origins(self):
        """Test CORS with different allowed origins"""
        origins = [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:5173',
            'http://127.0.0.1:5173'
        ]
        
        url = reverse('template-list')
        
        for origin in origins:
            with self.subTest(origin=origin):
                response = self.client.get(
                    url,
                    HTTP_ORIGIN=origin
                )
                
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn('Access-Control-Allow-Origin', response)
                self.assertEqual(
                    response['Access-Control-Allow-Origin'],
                    origin
                )
    
    def test_cors_disallowed_origin(self):
        """Test that disallowed origins are rejected"""
        url = reverse('template-list')
        
        response = self.client.get(
            url,
            HTTP_ORIGIN='http://malicious-site.com'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the origin is not in the allowed origins
        self.assertNotIn('Access-Control-Allow-Origin', response)
    
    def test_cors_with_authorization_header(self):
        """Test CORS with authorization header"""
        url = reverse('template-list')
        
        response = self.client.get(
            url,
            HTTP_ORIGIN='http://localhost:3000',
            HTTP_AUTHORIZATION='Bearer test-token'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Access-Control-Allow-Origin', response)
    
    @override_settings(CORS_ALLOWED_ORIGINS=['http://localhost:3000'])
    def test_cors_settings_override(self):
        """Test that CORS settings can be overridden"""
        url = reverse('template-list')
        
        # Test allowed origin
        response = self.client.get(
            url,
            HTTP_ORIGIN='http://localhost:3000'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Access-Control-Allow-Origin', response)
        
        # Test disallowed origin
        response = self.client.get(
            url,
            HTTP_ORIGIN='http://127.0.0.1:3000'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('Access-Control-Allow-Origin', response) 