#!/usr/bin/env python3
"""
Test runner for the Paystub Generator project.
Supports running different categories of tests and provides detailed output.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Setup Django environment for testing."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
    django.setup()

def run_tests(test_pattern=None, verbosity=2, interactive=True):
    """
    Run the test suite.
    
    Args:
        test_pattern: Specific test pattern to run (e.g., 'templates.tests.unit.test_api_views')
        verbosity: Test output verbosity (1=minimal, 2=normal, 3=verbose)
        interactive: Whether to run tests interactively
    """
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity, interactive=interactive, failfast=False)
    
    if test_pattern:
        # Run specific test pattern
        test_suite = test_runner.build_suite([test_pattern])
    else:
        # Run all tests
        test_suite = test_runner.build_suite()
    
    failures = test_runner.run_suite(test_suite)
    
    if failures:
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

def show_test_categories():
    """Display available test categories."""
    print("Available test categories:")
    print("=" * 50)
    print("📁 Unit Tests (templates/tests/unit/):")
    print("  • models          - Database models")
    print("  • serializers     - DRF serializers")
    print("  • services        - Business logic services")
    print("  • utils           - Utility functions")
    print()
    print("📁 Integration Tests (templates/tests/integration/):")
    print("  • views           - API and webhook views")
    print("  • workflows       - Complete user workflows")
    print()
    print("📁 Test Fixtures (templates/tests/fixtures/):")
    print("  • test_files      - Test PDF files and data")
    print()
    print("Usage examples:")
    print("  python run_tests.py all                    # Run all tests")
    print("  python run_tests.py models                 # Run model tests")
    print("  python run_tests.py services               # Run service tests")
    print("  python run_tests.py views                  # Run view tests")
    print("  python run_tests.py templates.tests.unit.test_api_views  # Run specific test file")

def main():
    """Main entry point for the test runner."""
    if len(sys.argv) < 2:
        show_test_categories()
        return
    
    command = sys.argv[1].lower()
    
    # Test category mappings
    test_categories = {
        'all': None,  # Run all tests
        'models': 'templates.tests.unit.test_models',
        'serializers': 'templates.tests.unit.test_serializers',
        'services': [
            'templates.tests.unit.test_pdf_service',
            'templates.tests.unit.test_stripe_service',
            'templates.tests.unit.test_email_service'
        ],
        'utils': 'templates.tests.unit.test_utils',
        'views': [
            'templates.tests.unit.test_api_views',
            'templates.tests.unit.test_webhook_views'
        ],
        'workflows': 'templates.tests.integration.tests',
        'unit': [
            'templates.tests.unit.test_models',
            'templates.tests.unit.test_serializers',
            'templates.tests.unit.test_pdf_service',
            'templates.tests.unit.test_stripe_service',
            'templates.tests.unit.test_email_service',
            'templates.tests.unit.test_utils',
            'templates.tests.unit.test_api_views',
            'templates.tests.unit.test_webhook_views'
        ],
        'integration': 'templates.tests.integration.tests',
        'help': None
    }
    
    if command == 'help':
        show_test_categories()
        return
    
    if command not in test_categories:
        print(f"❌ Unknown test category: {command}")
        print("Use 'python run_tests.py help' to see available categories.")
        sys.exit(1)
    
    test_patterns = test_categories[command]
    
    if test_patterns is None:
        # Run all tests
        run_tests()
    elif isinstance(test_patterns, list):
        # Run multiple test patterns
        for pattern in test_patterns:
            print(f"\n🧪 Running {pattern}...")
            run_tests(pattern)
    else:
        # Run single test pattern
        print(f"\n🧪 Running {test_patterns}...")
        run_tests(test_patterns)

if __name__ == '__main__':
    main() 