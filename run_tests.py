#!/usr/bin/env python3
"""
Test runner script for the PDF Generator Server

This script provides an easy way to run tests for the PDF service.
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

def run_pdf_service_tests():
    """Run tests specifically for the PDF service"""
    from django.core.management import execute_from_command_line
    
    print("🧪 Running PDF Service Tests...")
    print("=" * 50)
    
    # Run the main tests
    print("\n📋 Running main PDF service tests...")
    execute_from_command_line(['manage.py', 'test', 'templates.tests.PDFGenerationServiceTestCase', '-v', '2'])
    
    # Run integration tests
    print("\n🔗 Running integration tests...")
    execute_from_command_line(['manage.py', 'test', 'templates.tests.PDFServiceIntegrationTestCase', '-v', '2'])
    
    # Run real PDF file tests (if files exist)
    print("\n📄 Running real PDF file tests...")
    execute_from_command_line(['manage.py', 'test', 'templates.test_pdf_files', '-v', '2'])
    
    print("\n✅ All PDF service tests completed!")

def run_all_tests():
    """Run all tests"""
    from django.core.management import execute_from_command_line
    
    print("🧪 Running All Tests...")
    print("=" * 50)
    
    execute_from_command_line(['manage.py', 'test', '-v', '2'])
    
    print("\n✅ All tests completed!")

def run_specific_test(test_name):
    """Run a specific test"""
    from django.core.management import execute_from_command_line
    
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 50)
    
    execute_from_command_line(['manage.py', 'test', test_name, '-v', '2'])
    
    print(f"\n✅ Test {test_name} completed!")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'pdf':
            run_pdf_service_tests()
        elif command == 'all':
            run_all_tests()
        elif command == 'specific':
            if len(sys.argv) > 2:
                test_name = sys.argv[2]
                run_specific_test(test_name)
            else:
                print("❌ Please provide a test name: python run_tests.py specific <test_name>")
        else:
            print("❌ Unknown command. Use: pdf, all, or specific")
    else:
        print("🧪 PDF Generator Server Test Runner")
        print("=" * 40)
        print("Usage:")
        print("  python run_tests.py pdf      - Run PDF service tests only")
        print("  python run_tests.py all      - Run all tests")
        print("  python run_tests.py specific <test_name> - Run specific test")
        print("\nExamples:")
        print("  python run_tests.py pdf")
        print("  python run_tests.py specific templates.tests.PDFGenerationServiceTestCase.test_fill_pdf_template_with_form_fields") 