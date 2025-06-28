import io
from reportlab.pdfgen import canvas
from pdfrw import PdfReader, PdfWriter, PdfDict
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from templates.utils.w2_field_map import FIELD_MAP
import json


def decode_pdf_field_name(field):
    """Decode PDF field name from <FEFF...> format to readable string."""
    if isinstance(field, str) and field.startswith('<FEFF') and field.endswith('>'):
        hex_str = field[1:-1]  # Remove < and >
        hex_str = hex_str[4:]  # Remove FEFF
        bytes_data = bytes.fromhex(hex_str)
        return bytes_data.decode('utf-16-be')
    return field


class PDFGenerationService:
    """Service for generating filled PDFs from templates using reportlab and pdfrw"""
    
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
            
            # Read the template PDF using pdfrw
            pdf_reader = PdfReader(template_file)
            pdf_writer = PdfWriter()
            
            # Process each page
            for page_num, page in enumerate(pdf_reader.pages):
                # Get annotations (form fields) from the page
                annotations = page['/Annots']
                if annotations:
                    # Handle IndirectObject references
                    if hasattr(annotations, 'get_object'):
                        annotations = annotations.get_object()
                    
                    # Process each annotation
                    for annotation in annotations:
                        if annotation.Subtype == '/Widget':  # Form field
                            field_name = annotation.T
                            if field_name:
                                # Decode the field name if it's Unicode-encoded
                                decoded_field_name = decode_pdf_field_name(field_name)
                                
                                # Find the business field name using FIELD_MAP
                                business_field_name = None
                                for business_field, pdf_field in FIELD_MAP.items():
                                    if pdf_field == decoded_field_name:
                                        business_field_name = business_field
                                        break
                                
                                # Fill the field if we have data for it
                                if business_field_name and template_instance.data and business_field_name in template_instance.data:
                                    field_value = str(template_instance.data[business_field_name])
                                    annotation.update(PdfDict(V=field_value))
                                elif template_instance.data and decoded_field_name in template_instance.data:
                                    # Direct field name match (fallback)
                                    field_value = str(template_instance.data[decoded_field_name])
                                    annotation.update(PdfDict(V=field_value))
                
                # Add the page to the writer
                pdf_writer.addpage(page)
            
            # Write to bytes buffer
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            
            pdf_content = output_buffer.getvalue()
            
            return pdf_content
            
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
            saved_file = default_storage.save(filename, ContentFile(pdf_content))
            
            # Update template instance
            template_instance.file = filename
            template_instance.save()
            
            # Get the URL
            file_url = template_instance.file.url
            
            return file_url
            
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
        try:
            # Fill the PDF template
            pdf_content = PDFGenerationService.fill_pdf_template(template_instance)
            
            # Save the filled PDF
            pdf_url = PDFGenerationService.save_filled_pdf(template_instance, pdf_content)
            
            return pdf_url
            
        except Exception as e:
            raise e 