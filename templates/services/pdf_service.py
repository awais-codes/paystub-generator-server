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
    def fill_pdf_template(obj, use_preview_file=False):
        """
        Fill a PDF template with data and return the filled PDF as bytes
        Args:
            obj: TemplateInstance or TemplatePreview object with template and data
            use_preview_file: If True, use template.preview_file; else use template.file
        Returns:
            bytes: Filled PDF content
        """
        try:
            # Get the correct template file
            template_file = obj.template.preview_file if use_preview_file else obj.template.file
            if not template_file:
                raise ValueError("Template file not found")
            # Read the template PDF using pdfrw
            pdf_reader = PdfReader(template_file)
            pdf_writer = PdfWriter()
            # Process each page
            for page_num, page in enumerate(pdf_reader.pages):
                annotations = page['/Annots']
                if annotations:
                    if hasattr(annotations, 'get_object'):
                        annotations = annotations.get_object()
                    for annotation in annotations:
                        if annotation.Subtype == '/Widget':
                            field_name = annotation.T
                            if field_name:
                                decoded_field_name = decode_pdf_field_name(field_name)
                                business_field_name = None
                                for business_field, pdf_field in FIELD_MAP.items():
                                    if pdf_field == decoded_field_name:
                                        business_field_name = business_field
                                        break
                                if business_field_name and obj.data and business_field_name in obj.data:
                                    field_value = str(obj.data[business_field_name])
                                    annotation.update(PdfDict(V=field_value))
                                elif obj.data and decoded_field_name in obj.data:
                                    field_value = str(obj.data[decoded_field_name])
                                    annotation.update(PdfDict(V=field_value))
                pdf_writer.addpage(page)
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            pdf_content = output_buffer.getvalue()
            return pdf_content
        except Exception as e:
            raise Exception(f"Error filling PDF template: {str(e)}")

    @staticmethod
    def save_filled_pdf(obj, pdf_content):
        """
        Save the filled PDF to S3 and update the object (TemplateInstance or TemplatePreview)
        Args:
            obj: TemplateInstance or TemplatePreview
            pdf_content: PDF content as bytes
        Returns:
            str: URL of the saved PDF
        """
        try:
            # Generate filename
            if obj.__class__.__name__ == 'TemplateInstance':
                filename = f"templates-instances/{obj.id}.pdf"
            else:
                filename = f"template-previews/{obj.id}.pdf"
            # Save to S3
            saved_file = default_storage.save(filename, ContentFile(pdf_content))
            # Update object
            obj.file = filename
            obj.save()
            file_url = obj.file.url
            return file_url
        except Exception as e:
            raise Exception(f"Error saving filled PDF: {str(e)}")

    @staticmethod
    def generate_pdf(obj, use_preview_file=False):
        """
        Complete PDF generation process: fill template and save to S3
        Args:
            obj: TemplateInstance or TemplatePreview
            use_preview_file: If True, use template.preview_file; else use template.file
        Returns:
            str: URL of the generated PDF
        """
        try:
            pdf_content = PDFGenerationService.fill_pdf_template(obj, use_preview_file=use_preview_file)
            pdf_url = PDFGenerationService.save_filled_pdf(obj, pdf_content)
            return pdf_url
        except Exception as e:
            raise e 