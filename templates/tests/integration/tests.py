from django.test import TestCase, override_settings
import io
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import PyPDF2

from .models import Template, TemplateInstance
from .services.pdf_service import PDFGenerationService


class PDFGenerationServiceTestCase(TestCase):
    """Test cases for PDFGenerationService"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test template
        self.template = Template.objects.create(
            name="Test Paystub Template",
            description="A test template for paystub generation"
        )
        
        # Create test data
        self.test_data = {
            "EmployeeName": "John Doe",
            "SSN": "123-45-6789",
            "GrossPay": "5000.00",
            "NetPay": "3500.00",
            "PayPeriod": "Bi-weekly"
        }
        
        # Create a template instance
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data=self.test_data
        )
    
    def create_test_pdf_with_form_fields(self):
        """Create a test PDF with form fields for testing"""
        # Create a simple PDF with form fields using PyPDF2
        pdf_writer = PyPDF2.PdfWriter()
        
        # Create a page
        page = PyPDF2.PageObject.create_blank_page(width=612, height=792)
        
        # Create form fields
        fields = []
        
        # Employee Name field
        name_field = PyPDF2.generic.DictionaryObject()
        name_field.update({
            PyPDF2.generic.NameObject('/FT'): PyPDF2.generic.NameObject('/Tx'),
            PyPDF2.generic.NameObject('/T'): PyPDF2.generic.createStringObject('EmployeeName'),
            PyPDF2.generic.NameObject('/V'): PyPDF2.generic.createStringObject(''),
            PyPDF2.generic.NameObject('/F'): PyPDF2.generic.NumberObject(4),
            PyPDF2.generic.NameObject('/Rect'): PyPDF2.generic.ArrayObject([
                PyPDF2.generic.FloatObject(100),
                PyPDF2.generic.FloatObject(700),
                PyPDF2.generic.FloatObject(300),
                PyPDF2.generic.FloatObject(720)
            ])
        })
        fields.append(name_field)
        
        # SSN field
        ssn_field = PyPDF2.generic.DictionaryObject()
        ssn_field.update({
            PyPDF2.generic.NameObject('/FT'): PyPDF2.generic.NameObject('/Tx'),
            PyPDF2.generic.NameObject('/T'): PyPDF2.generic.createStringObject('SSN'),
            PyPDF2.generic.NameObject('/V'): PyPDF2.generic.createStringObject(''),
            PyPDF2.generic.NameObject('/F'): PyPDF2.generic.NumberObject(4),
            PyPDF2.generic.NameObject('/Rect'): PyPDF2.generic.ArrayObject([
                PyPDF2.generic.FloatObject(100),
                PyPDF2.generic.FloatObject(650),
                PyPDF2.generic.FloatObject(300),
                PyPDF2.generic.FloatObject(670)
            ])
        })
        fields.append(ssn_field)
        
        # Create AcroForm
        acro_form = PyPDF2.generic.DictionaryObject()
        acro_form.update({
            PyPDF2.generic.NameObject('/Fields'): PyPDF2.generic.ArrayObject(fields),
            PyPDF2.generic.NameObject('/NeedAppearances'): PyPDF2.generic.BooleanObject(True)
        })
        
        # Add AcroForm to page
        page[PyPDF2.generic.NameObject('/AcroForm')] = acro_form
        
        # Add page to writer
        pdf_writer.add_page(page)
        
        # Write to bytes
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
    
    @patch('templates.services.pdf_service.default_storage')
    def test_fill_pdf_template_with_form_fields(self, mock_storage):
        """Test filling PDF template with form fields"""
        # Create test PDF content
        pdf_content = self.create_test_pdf_with_form_fields()
        
        # Save the file properly using Django's file.save() method
        self.template.file.save('test_template.pdf', ContentFile(pdf_content))
        
        # Test filling the PDF
        result = PDFGenerationService.fill_pdf_template(self.template_instance)
        
        # Verify result is bytes
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)
        
        # Verify the PDF can be read
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(result))
        self.assertEqual(len(pdf_reader.pages), 1)
    
    def test_fill_pdf_template_no_template_file(self):
        """Test filling PDF template when template file is missing"""
        # Ensure template has no file
        self.template.file = None
        self.template.save()
        
        with self.assertRaises(Exception) as context:
            PDFGenerationService.fill_pdf_template(self.template_instance)
        
        self.assertIn("Template file not found", str(context.exception))
    
    def test_fill_pdf_template_with_invalid_pdf(self):
        """Test filling PDF template with invalid PDF content"""
        # Create invalid PDF content
        invalid_pdf_content = b"Invalid PDF content"
        
        # Save the file properly using Django's file.save() method
        self.template.file.save('invalid_template.pdf', ContentFile(invalid_pdf_content))
        
        with self.assertRaises(Exception) as context:
            PDFGenerationService.fill_pdf_template(self.template_instance)
        
        self.assertIn("Error filling PDF template", str(context.exception))
    
    @patch('templates.services.pdf_service.default_storage')
    def test_save_filled_pdf(self, mock_storage):
        """Test saving filled PDF to storage"""
        # Mock storage save method
        mock_storage.save.return_value = "templates-instances/test-uuid.pdf"
        
        # Test PDF content
        pdf_content = b"Test PDF content"
        
        # Test saving
        result = PDFGenerationService.save_filled_pdf(self.template_instance, pdf_content)
        
        # Verify storage.save was called
        mock_storage.save.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_storage.save.call_args
        self.assertIn("templates-instances/", call_args[0][0])  # filename
        self.assertIsInstance(call_args[0][1], ContentFile)  # content
        
        # Verify template instance was updated
        self.template_instance.refresh_from_db()
        self.assertIsNotNone(self.template_instance.file)
    
    @patch('templates.services.pdf_service.default_storage')
    def test_save_filled_pdf_storage_error(self, mock_storage):
        """Test saving filled PDF when storage fails"""
        # Mock storage to raise an exception
        mock_storage.save.side_effect = Exception("Storage error")
        
        pdf_content = b"Test PDF content"
        
        with self.assertRaises(Exception) as context:
            PDFGenerationService.save_filled_pdf(self.template_instance, pdf_content)
        
        self.assertIn("Error saving filled PDF", str(context.exception))
    
    @patch('templates.services.pdf_service.default_storage')
    def test_generate_pdf_complete_process(self, mock_storage):
        """Test complete PDF generation process"""
        # Create test PDF content
        pdf_content = self.create_test_pdf_with_form_fields()
        
        # Save the file properly using Django's file.save() method
        self.template.file.save('test_template.pdf', ContentFile(pdf_content))
        
        # Mock storage
        mock_storage.save.return_value = "templates-instances/test-uuid.pdf"
        
        # Test complete generation
        result = PDFGenerationService.generate_pdf(self.template_instance)
        
        # Verify result is a string (URL)
        self.assertIsInstance(result, str)
        
        # Verify storage was called
        mock_storage.save.assert_called_once()
        
        # Verify template instance was updated
        self.template_instance.refresh_from_db()
        self.assertIsNotNone(self.template_instance.file)
    
    def test_generate_pdf_with_empty_data(self):
        """Test PDF generation with empty data"""
        # Set empty data
        self.template_instance.data = {}
        self.template_instance.save()
        
        # Create test PDF content
        pdf_content = self.create_test_pdf_with_form_fields()
        
        # Save the file properly using Django's file.save() method
        self.template.file.save('test_template.pdf', ContentFile(pdf_content))
        
        # Test generation (should not fail with empty data)
        with patch('templates.services.pdf_service.default_storage') as mock_storage:
            mock_storage.save.return_value = "templates-instances/test-uuid.pdf"
            
            result = PDFGenerationService.generate_pdf(self.template_instance)
            self.assertIsInstance(result, str)
    
    def test_generate_pdf_with_none_data(self):
        """Test PDF generation with None data"""
        # Set None data
        self.template_instance.data = None
        self.template_instance.save()
        
        # Create test PDF content
        pdf_content = self.create_test_pdf_with_form_fields()
        
        # Save the file properly using Django's file.save() method
        self.template.file.save('test_template.pdf', ContentFile(pdf_content))
        
        # Test generation (should handle None data gracefully)
        with patch('templates.services.pdf_service.default_storage') as mock_storage:
            mock_storage.save.return_value = "templates-instances/test-uuid.pdf"
            
            result = PDFGenerationService.generate_pdf(self.template_instance)
            self.assertIsInstance(result, str)


class PDFServiceIntegrationTestCase(TestCase):
    """Integration tests for PDF service with real file operations"""
    
    def setUp(self):
        """Set up test data"""
        self.template = Template.objects.create(
            name="Integration Test Template",
            description="Template for integration testing"
        )
        
        self.test_data = {
            "EmployeeName": "Jane Smith",
            "SSN": "987-65-4321",
            "GrossPay": "7500.00",
            "NetPay": "5250.00"
        }
        
        self.template_instance = TemplateInstance.objects.create(
            template=self.template,
            data=self.test_data
        )
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_pdf_generation_with_real_file(self):
        """Test PDF generation with a real file (if available)"""
        # This test will work if you provide a test PDF file
        # For now, we'll create a simple test PDF
        
        # Create a simple PDF for testing
        pdf_writer = PyPDF2.PdfWriter()
        page = PyPDF2.PageObject.create_blank_page(width=612, height=792)
        pdf_writer.add_page(page)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            pdf_writer.write(temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Create a SimpleUploadedFile
            with open(temp_file_path, 'rb') as f:
                uploaded_file = SimpleUploadedFile(
                    "test_template.pdf",
                    f.read(),
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
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


# Test utilities for creating test PDFs
class PDFTestUtils:
    """Utility class for creating test PDFs"""
    
    @staticmethod
    def create_simple_pdf():
        """Create a simple PDF without form fields"""
        pdf_writer = PyPDF2.PdfWriter()
        page = PyPDF2.PageObject.create_blank_page(width=612, height=792)
        pdf_writer.add_page(page)
        
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
    
    @staticmethod
    def create_pdf_with_form_fields(field_names):
        """Create a PDF with specific form fields"""
        pdf_writer = PyPDF2.PdfWriter()
        page = PyPDF2.PageObject.create_blank_page(width=612, height=792)
        
        fields = []
        y_position = 700
        
        for field_name in field_names:
            field = PyPDF2.generic.DictionaryObject()
            field.update({
                PyPDF2.generic.NameObject('/FT'): PyPDF2.generic.NameObject('/Tx'),
                PyPDF2.generic.NameObject('/T'): PyPDF2.generic.createStringObject(field_name),
                PyPDF2.generic.NameObject('/V'): PyPDF2.generic.createStringObject(''),
                PyPDF2.generic.NameObject('/F'): PyPDF2.generic.NumberObject(4),
                PyPDF2.generic.NameObject('/Rect'): PyPDF2.generic.ArrayObject([
                    PyPDF2.generic.FloatObject(100),
                    PyPDF2.generic.FloatObject(y_position),
                    PyPDF2.generic.FloatObject(300),
                    PyPDF2.generic.FloatObject(y_position + 20)
                ])
            })
            fields.append(field)
            y_position -= 50
        
        acro_form = PyPDF2.generic.DictionaryObject()
        acro_form.update({
            PyPDF2.generic.NameObject('/Fields'): PyPDF2.generic.ArrayObject(fields),
            PyPDF2.generic.NameObject('/NeedAppearances'): PyPDF2.generic.BooleanObject(True)
        })
        
        page[PyPDF2.generic.NameObject('/AcroForm')] = acro_form
        pdf_writer.add_page(page)
        
        output_buffer = io.BytesIO()
        pdf_writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
