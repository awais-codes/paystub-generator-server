#!/usr/bin/env python3
"""
Enhanced test runner for the paystub generator server
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

def run_tests(category='all', specific_test=None):
    """
    Run tests based on category or specific test
    
    Args:
        category: Test category ('all', 'services', 'views', 'unit', 'integration', 'w2')
        specific_test: Specific test to run (e.g., 'templates.tests.unit.test_w2_pdf_generation')
    """
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    if specific_test:
        # Run specific test
        print(f"Running specific test: {specific_test}")
        test_labels = [specific_test]
    else:
        # Run tests by category
        if category == 'all':
            test_labels = ['templates.tests']
        elif category == 'services':
            test_labels = [
                'templates.tests.unit.test_pdf_files',
                'templates.tests.unit.test_stripe_service', 
                'templates.tests.unit.test_email_service'
            ]
        elif category == 'views':
            test_labels = [
                'templates.tests.unit.test_api_views',
                'templates.tests.unit.test_webhook_views'
            ]
        elif category == 'unit':
            test_labels = [
                'templates.tests.unit.test_pdf_files',
                'templates.tests.unit.test_stripe_service',
                'templates.tests.unit.test_email_service',
                'templates.tests.unit.test_api_views',
                'templates.tests.unit.test_webhook_views',
                'templates.tests.unit.test_utils',
                'templates.tests.unit.test_w2_pdf_generation'
            ]
        elif category == 'integration':
            test_labels = ['templates.tests.integration.tests']
        elif category == 'w2':
            test_labels = ['templates.tests.unit.test_w2_pdf_generation']
        else:
            print(f"Unknown category: {category}")
            print("Available categories: all, services, views, unit, integration, w2")
            return
    
    # Run the tests
    failures = test_runner.run_tests(test_labels)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return 1
    else:
        print(f"\n✅ All tests passed!")
        return 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            # Specific test
            result = run_tests(specific_test=sys.argv[2])
        else:
            # Category
            result = run_tests(category=sys.argv[1])
    else:
        # Default: run all tests
        result = run_tests()
    
    sys.exit(result) 