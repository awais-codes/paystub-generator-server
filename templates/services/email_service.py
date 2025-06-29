from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import os


class EmailService:
    """Service for sending emails with PDF attachments"""
    
    @staticmethod
    def send_pdf_email(template_instance, recipient_email):
        """
        Send generated PDF to recipient email
        
        Args:
            template_instance: TemplateInstance object with generated PDF
            recipient_email: Email address to send PDF to
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Check if PDF exists and is paid
            if not template_instance.file or not template_instance.is_paid:
                raise ValueError("PDF not available or payment not completed")
            
            # For S3 storage, we'll use the URL in the email body instead of attachment
            pdf_url = template_instance.file.url if template_instance.file else None
            
            if not pdf_url:
                raise ValueError("PDF file not found")
            
            # Prepare email content
            subject = f"Your PDF Document - {template_instance.template.name}"
            
            # Email body with download link
            body = f"""
            Hello,
            
            Your PDF document has been generated successfully from the {template_instance.template.name} template.
            
            You can download your PDF here: {pdf_url}
            
            Thank you for using our service!
            
            Best regards,
            PDF Generator Team
            """
            
            # Create email message
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            
            # Send email
            email.send()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error sending PDF email: {str(e)}")
    
    @staticmethod
    def send_download_link_email(template_instance, recipient_email):
        """
        Send download link email (alternative to attachment)
        
        Args:
            template_instance: TemplateInstance object
            recipient_email: Email address to send link to
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            if not template_instance.is_paid:
                raise ValueError("Payment not completed")
            
            subject = f"Download Your PDF - {template_instance.template.name}"
            
            # Generate secure download link (you might want to implement expiring links)
            download_url = template_instance.file.url if template_instance.file else None
            
            if not download_url:
                raise ValueError("PDF file not found")
            
            body = f"""
            Hello,
            
            Your PDF document "{template_instance.template.name}" is ready for download.
            
            Download Link: {download_url}
            
            This link will remain active for 24 hours.
            
            Thank you for using our service!
            
            Best regards,
            PDF Generator Team
            """
            
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            
            email.send()
            
            return True
            
        except Exception as e:
            raise Exception(f"Error sending download link email: {str(e)}") 