import io
import PyPDF2
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import json


class PDFGenerationService:
    """Service for generating filled PDFs from templates"""
    
    @staticmethod
    def fill_pdf_template(template_instance):
        """
        Fill a PDF template with data and return the filled PDF as bytes
        
        Args:
            template_instance: TemplateInstance object with template and data
            
        Returns:
            bytes: Filled PDF content
        """
        try:
            # Get the template file from S3
            template_file = template_instance.template.file
            
            if not template_file:
                raise ValueError("Template file not found")
            
            # Read the template PDF
            pdf_reader = PyPDF2.PdfReader(template_file)
            pdf_writer = PyPDF2.PdfWriter()
            
            # Get the first page (assuming single page templates)
            page = pdf_reader.pages[0]
            
            # Fill form fields if they exist
            if '/AcroForm' in page and '/Fields' in page['/AcroForm']:
                fields = page['/AcroForm']['/Fields']
                for field in fields:
                    if '/T' in field:  # Field name
                        field_name = field['/T']
                        # Handle None data gracefully
                        if template_instance.data and field_name in template_instance.data:
                            field_value = str(template_instance.data[field_name])
                            # Use the correct PyPDF2 API for updating field values
                            field[PyPDF2.generic.NameObject('/V')] = PyPDF2.generic.createStringObject(field_value)
            
            # Add the filled page to the writer
            pdf_writer.add_page(page)
            
            # Write to bytes buffer
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Error filling PDF template: {str(e)}")
    
    @staticmethod
    def save_filled_pdf(template_instance, pdf_content):
        """
        Save the filled PDF to S3 and update the template instance
        
        Args:
            template_instance: TemplateInstance object
            pdf_content: PDF content as bytes
            
        Returns:
            str: URL of the saved PDF
        """
        try:
            # Generate filename
            filename = f"templates-instances/{template_instance.id}.pdf"
            
            # Save to S3
            default_storage.save(filename, ContentFile(pdf_content))
            
            # Update template instance
            template_instance.file = filename
            template_instance.save()
            
            return template_instance.file.url
            
        except Exception as e:
            raise Exception(f"Error saving filled PDF: {str(e)}")
    
    @staticmethod
    def generate_pdf(template_instance):
        """
        Complete PDF generation process: fill template and save to S3
        
        Args:
            template_instance: TemplateInstance object with template and data
            
        Returns:
            str: URL of the generated PDF
        """
        # Fill the PDF template
        pdf_content = PDFGenerationService.fill_pdf_template(template_instance)
        
        # Save the filled PDF
        pdf_url = PDFGenerationService.save_filled_pdf(template_instance, pdf_content)
        
        return pdf_url 