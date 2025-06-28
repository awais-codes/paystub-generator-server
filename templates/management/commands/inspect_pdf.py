from django.core.management.base import BaseCommand
from templates.utils.pdf_inspector import PDFInspector
import os


class Command(BaseCommand):
    help = 'Inspect PDF form fields and suggest field mappings'

    def add_arguments(self, parser):
        parser.add_argument('pdf_path', type=str, help='Path to the PDF file to inspect')
        parser.add_argument(
            '--comprehensive',
            action='store_true',
            help='Run comprehensive analysis including PDF structure'
        )

    def handle(self, *args, **options):
        pdf_path = options['pdf_path']
        
        if not os.path.exists(pdf_path):
            self.stdout.write(
                self.style.ERROR(f'PDF file not found: {pdf_path}')
            )
            return
        
        try:
            self.stdout.write(f'Inspecting PDF: {pdf_path}')
            self.stdout.write('=' * 60)
            
            if options['comprehensive']:
                PDFInspector.print_comprehensive_analysis(pdf_path)
            else:
                PDFInspector.print_field_analysis(pdf_path)
            
            self.stdout.write(
                self.style.SUCCESS('PDF inspection completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error inspecting PDF: {str(e)}')
            ) 