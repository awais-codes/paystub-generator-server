import os
import io
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from pdfrw import PdfReader

from templates.models import Template, TemplateInstance
from templates.services.pdf_service import PDFGenerationService


class RealPDFFileTestCase(TestCase):
    """Test cases for PDF service using real PDF files"""
    
    def setUp(self):
        """Set up test data"""
        self.template = Template.objects.create(
            name="Real PDF Test Template",
            description="Template for testing with real PDF files"
        )
        
        self.test_data = {
            "EmployeeName": "John Doe",
            "SSN": "123-45-6789",
            "GrossPay": "5000.00",
            "NetPay": "3500.00",
            "PayPeriod": "Bi-weekly",
            "PayDate": "2024-01-15"
        }
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data=self.test_data
        )
    
    def test_with_real_paystub_template(self):
        """Test PDF generation with a real paystub template file"""
        # Path to test PDF file (you can add this to your repository)
        test_pdf_path = os.path.join(
            os.path.dirname(__file__), 
            'test_files', 
            'paystub_template.pdf'
        )
        
        # Skip test if file doesn't exist
        if not os.path.exists(test_pdf_path):
            self.skipTest("Test PDF file not found. Add a paystub_template.pdf to templates/test_files/")
        
        # Load the real PDF file
        with open(test_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Create uploaded file
        uploaded_file = SimpleUploadedFile(
            "paystub_template.pdf",
            pdf_content,
            content_type="application/pdf"
        )
        
        # Assign to template
        self.template.file = uploaded_file
        self.template.save()
        
        # Test PDF generation
        with patch('templates.services.pdf_service.default_storage') as mock_storage:
            mock_storage.save.return_value = "templates-instances/test-uuid.pdf"
            
            result = PDFGenerationService.generate_pdf(self.template_instance)
            
            # Verify result
            self.assertIsInstance(result, str)
            mock_storage.save.assert_called_once()
            
            # Verify the generated PDF can be read
            call_args = mock_storage.save.call_args
            saved_content = call_args[0][1].read()
            
            # Verify it's a valid PDF using pdfrw
            pdf_reader = PdfReader(io.BytesIO(saved_content))
            self.assertGreater(len(pdf_reader.pages), 0)
    
    def test_form_field_extraction(self):
        """Test extracting form fields from a real PDF template"""
        test_pdf_path = os.path.join(
            os.path.dirname(__file__), 
            'test_files', 
            'paystub_template.pdf'
        )
        
        if not os.path.exists(test_pdf_path):
            self.skipTest("Test PDF file not found")
        
        # Load the PDF and extract form fields using pdfrw
        with open(test_pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            page = pdf_reader.pages[0]
            
            # Check if PDF has annotations (form fields)
            annotations = page['/Annots']
            field_names = []
            
            if annotations:
                # Handle IndirectObject references
                if hasattr(annotations, 'get_object'):
                    annotations = annotations.get_object()
                
                for annotation in annotations:
                    if annotation.Subtype == '/Widget':  # Form field
                        field_name = annotation.T
                        if field_name:
                            field_names.append(field_name)
            
            # Verify we found some form fields
            self.assertGreater(len(field_names), 0)
            
            # Print field names for debugging
            print(f"Found form fields: {field_names}")
            
            # Test that our test data has matching fields
            matching_fields = [name for name in field_names if name in self.test_data]
            self.assertGreater(len(matching_fields), 0, 
                             f"No matching fields found. Available: {field_names}")
    
    def test_pdf_with_different_data_sets(self):
        """Test PDF generation with different data sets"""
        test_pdf_path = os.path.join(
            os.path.dirname(__file__), 
            'test_files', 
            'paystub_template.pdf'
        )
        
        if not os.path.exists(test_pdf_path):
            self.skipTest("Test PDF file not found")
        
        # Load the real PDF file
        with open(test_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        uploaded_file = SimpleUploadedFile(
            "paystub_template.pdf",
            pdf_content,
            content_type="application/pdf"
        )
        
        self.template.file = uploaded_file
        self.template.save()
        
        # Test with different data sets
        test_cases = [
            {
                "name": "Minimal data",
                "data": {"EmployeeName": "Jane Smith"}
            },
            {
                "name": "Complete data",
                "data": {
                    "EmployeeName": "Bob Johnson",
                    "SSN": "111-22-3333",
                    "GrossPay": "8000.00",
                    "NetPay": "5600.00",
                    "PayPeriod": "Monthly",
                    "PayDate": "2024-02-01"
                }
            },
            {
                "name": "Empty data",
                "data": {}
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(test_case["name"]):
                # Update template instance data
                self.template_instance.data = test_case["data"]
                self.template_instance.save()
                
                # Test generation
                with patch('templates.services.pdf_service.default_storage') as mock_storage:
                    mock_storage.save.return_value = "templates-instances/test-uuid.pdf"
                    
                    result = PDFGenerationService.generate_pdf(self.template_instance)
                    
                    # Verify result
                    self.assertIsInstance(result, str)
                    mock_storage.save.assert_called_once()
                    
                    # Reset mock for next iteration
                    mock_storage.reset_mock()


class PDFValidationTestCase(TestCase):
    """Test cases for PDF validation and error handling"""
    
    def setUp(self):
        """Set up test data"""
        self.template = Template.objects.create(
            name="Validation Test Template",
            description="Template for validation testing"
        )
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data={"EmployeeName": "Test User"}
        )
    
    def test_corrupted_pdf_handling(self):
        """Test handling of corrupted PDF files"""
        # Create corrupted PDF content
        corrupted_content = b"This is not a valid PDF file"
        
        uploaded_file = SimpleUploadedFile(
            "corrupted.pdf",
            corrupted_content,
            content_type="application/pdf"
        )
        
        self.template.file = uploaded_file
        self.template.save()
        
        # Test that it raises an exception
        with self.assertRaises(Exception) as context:
            PDFGenerationService.generate_pdf(self.template_instance)
        
        self.assertIn("Error filling PDF template", str(context.exception))
    
    def test_pdf_without_form_fields(self):
        """Test PDF generation with a PDF that has no form fields"""
        # Create a simple PDF without form fields using reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        output_buffer = io.BytesIO()
        c = canvas.Canvas(output_buffer, pagesize=letter)
        c.drawString(100, 750, "Simple PDF without form fields")
        c.save()
        output_buffer.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "simple.pdf",
            output_buffer.getvalue(),
            content_type="application/pdf"
        )
        
        self.template.file = uploaded_file
        self.template.save()
        
        # Test generation (should not fail, just not fill any fields)
        with patch('templates.services.pdf_service.default_storage') as mock_storage:
            mock_storage.save.return_value = "templates-instances/test-uuid.pdf"
            
            result = PDFGenerationService.generate_pdf(self.template_instance)
            
            # Should still generate a PDF
            self.assertIsInstance(result, str)
            mock_storage.save.assert_called_once()


# Instructions for adding test PDF files
"""
To use these tests with real PDF files:

1. Create a directory: templates/test_files/
2. Add your test PDF file(s) to this directory
3. Recommended files:
   - paystub_template.pdf (with form fields like EmployeeName, SSN, etc.)
   - w2_template.pdf (W2 form template)
   - 1099_template.pdf (1099 form template)

4. The tests will automatically detect and use these files if they exist.

Example directory structure:
templates/
├── test_files/
│   ├── paystub_template.pdf
│   ├── w2_template.pdf
│   └── 1099_template.pdf
├── tests.py
└── test_pdf_files.py

The tests will skip if files are not found, so they won't break your CI/CD pipeline.
""" 