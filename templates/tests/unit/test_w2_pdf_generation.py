from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from templates.models import Template, TemplateInstance
from templates.services.pdf_service import PDFGenerationService
from templates.utils.w2_field_map import FIELD_MAP
import os


class W2PDFGenerationTestCase(TestCase):
    """Test W2 PDF generation with field mappings"""
    
    def setUp(self):
        """Set up test data"""
        # Create a test template
        self.template = Template.objects.create(
            name='W2 Form Template',
            description='Test W2 form template'
        )
        
        # Upload the W2 template file
        w2_template_path = 'templates/tests/fixtures/test_files/w2_template.pdf'
        if os.path.exists(w2_template_path):
            with open(w2_template_path, 'rb') as f:
                file_content = f.read()
            
            self.template.file = SimpleUploadedFile(
                'w2_template.pdf',
                file_content,
                content_type='application/pdf'
            )
            self.template.save()
    
    def test_w2_pdf_generation_with_mappings(self):
        """Test that W2 PDF can be generated using field mappings"""
        if not self.template.file:
            self.skipTest("W2 template file not available")
        
        # Create test data using the mapped field names
        test_data = {
            'employee_ssn': '123-45-6789',
            'employee_ein': '12-3456789',
            'employer_name_address_zip': 'Test Company, 123 Main St, City, ST 12345',
            'control_number': '123456789',
            'firt_name_and_initial': 'John A',
            'last_name': 'Doe',
            'stuff': 'Additional info',
            'adress_and_code': '456 Oak Ave, Town, ST 67890',
            'wages_tips': '50000.00',
            'fed_income_tax_withheld': '8000.00',
            'social_security_wages': '50000.00',
            'social_security_wages_withheld': '3100.00',
            'medicare_wages': '50000.00',
            'medicare_tax_witheld': '725.00',
            'social_security_tips': '0.00',
            'allocated_tips': '0.00',
            'dependent_care_benefits': '0.00',
            'non_qualified_plans': '0.00',
            'twelve_a_0': '1000.00',
            'twelve_a_1': '1000.00',
            'twelve_b_0': '2000.00',
            'twelve_b_1': '2000.00',
            'twelve_c_0': '3000.00',
            'twelve_c_1': '3000.00',
            'twelve_d_0': '4000.00',
            'twelve_d_1': '4000.00',
            'other': 'Other info',
            'state_1': 'CA',
            'state_1_employee_id': 'CA123456',
            'state_2': 'NY',
            'state_2_employee_id': 'NY789012',
            'state_1_wages_tips': '50000.00',
            'state_2_wages_tips': '0.00',
            'state_1_income_tax': '2500.00',
            'state_2_income_tax': '0.00',
            'state_1_local_wages_tips': '50000.00',
            'state_2_local_wages_tips': '0.00',
            'state_1_local_income_tax': '500.00',
            'state_2_local_income_tax': '0.00',
            'state_1_locality_name': 'Los Angeles',
            'state_2_locality_name': '',
            'void': False,
            'statutory_employee': False,
            'retirement_plan': True,
            'third_party_sick_pay': False,
        }
        
        # Create a template instance
        template_instance = TemplateInstance.objects.create(
            template=self.template,
            data=test_data
        )
        
        try:
            # Generate the PDF
            pdf_url = PDFGenerationService.generate_pdf(template_instance)
            
            # Verify the PDF was generated
            self.assertIsNotNone(pdf_url)
            self.assertTrue(pdf_url.startswith('http'))  # Should be a valid URL
            self.assertIn('.pdf', pdf_url)  # Should contain .pdf in the URL
            
            # Verify the template instance was updated
            template_instance.refresh_from_db()
            self.assertIsNotNone(template_instance.file)
            self.assertTrue(template_instance.file.name.endswith('.pdf'))
            
            print(f"✅ W2 PDF generated successfully: {pdf_url}")
            
        except Exception as e:
            self.fail(f"PDF generation failed: {str(e)}")
    
    def test_w2_pdf_generation_with_f2_fields(self):
        """Test that W2 PDF can be generated using f2_* field mappings"""
        if not self.template.file:
            self.skipTest("W2 template file not available")
        
        # Create test data using the f2_* mapped field names
        test_data = {
            'employee_ssn_2': '987-65-4321',
            'employee_ein_2': '98-7654321',
            'employer_name_address_zip_2': 'Test Company 2, 456 Second St, City, ST 54321',
            'control_number_2': '987654321',
            'firt_name_and_initial_2': 'Jane B',
            'last_name_2': 'Smith',
            'wages_tips_2': '60000.00',
            'fed_income_tax_withheld_2': '10000.00',
            'social_security_wages_2': '60000.00',
            'social_security_wages_withheld_2': '3720.00',
            'medicare_wages_2': '60000.00',
            'medicare_tax_witheld_2': '870.00',
            'void_2': False,
            'statutory_employee_2': False,
            'retirement_plan_2': True,
            'third_party_sick_pay_2': False,
        }
        
        # Create a template instance
        template_instance = TemplateInstance.objects.create(
            template=self.template,
            data=test_data
        )
        
        try:
            # Generate the PDF
            pdf_url = PDFGenerationService.generate_pdf(template_instance)
            
            # Verify the PDF was generated
            self.assertIsNotNone(pdf_url)
            self.assertTrue(pdf_url.startswith('http'))  # Should be a valid URL
            self.assertIn('.pdf', pdf_url)  # Should contain .pdf in the URL
            
            print(f"✅ W2 PDF with f2_* fields generated successfully: {pdf_url}")
            
        except Exception as e:
            self.fail(f"PDF generation with f2_* fields failed: {str(e)}")
    
    def test_field_mapping_coverage(self):
        """Test that all mapped fields are properly handled"""
        # Check that all mapped fields have valid PDF field names
        for business_field, pdf_field in FIELD_MAP.items():
            self.assertIsInstance(business_field, str)
            self.assertIsInstance(pdf_field, str)
            self.assertTrue(pdf_field.startswith(('f1_', 'f2_', 'c1_', 'c2_')))
            self.assertTrue(pdf_field.endswith('[0]'))
        
        print(f"✅ Field mapping validation passed for {len(FIELD_MAP)} fields")
    
    def test_minimal_w2_data(self):
        """Test PDF generation with minimal required W2 data"""
        if not self.template.file:
            self.skipTest("W2 template file not available")
        
        # Minimal test data with just a few key fields
        minimal_data = {
            'employee_ssn': '111-22-3333',
            'firt_name_and_initial': 'Test',
            'last_name': 'User',
            'wages_tips': '10000.00',
            'fed_income_tax_withheld': '1000.00',
        }
        
        # Create a template instance
        template_instance = TemplateInstance.objects.create(
            template=self.template,
            data=minimal_data
        )
        
        try:
            # Generate the PDF
            pdf_url = PDFGenerationService.generate_pdf(template_instance)
            
            # Verify the PDF was generated
            self.assertIsNotNone(pdf_url)
            self.assertTrue(pdf_url.startswith('http'))  # Should be a valid URL
            self.assertIn('.pdf', pdf_url)  # Should contain .pdf in the URL
            
            print(f"✅ Minimal W2 PDF generated successfully: {pdf_url}")
            
        except Exception as e:
            self.fail(f"Minimal PDF generation failed: {str(e)}") 