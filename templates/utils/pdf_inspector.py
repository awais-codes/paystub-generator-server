from pdfrw import PdfReader
from django.core.files.base import ContentFile


class PDFInspector:
    """Utility to inspect PDF form fields and help with field mapping"""
    
    @staticmethod
    def inspect_form_fields(pdf_file):
        """
        Inspect all form fields in a PDF and return their names and types
        
        Args:
            pdf_file: PDF file object or path
            
        Returns:
            dict: Dictionary with field information
        """
        try:
            # Read the PDF using pdfrw
            pdf_reader = PdfReader(pdf_file)
            
            fields_info = {}
            
            def extract_fields_from_object(obj, prefix=""):
                """Recursively extract fields from form objects"""
                if hasattr(obj, 'get_object'):
                    obj = obj.get_object()
                
                if isinstance(obj, dict):
                    # Check if this is a field
                    if '/T' in obj:
                        field_name = obj['/T']
                        field_type = obj.get('/FT', 'Unknown')
                        field_value = obj.get('/V', '')
                        
                        full_name = f"{prefix}{field_name}" if prefix else field_name
                        fields_info[full_name] = {
                            'type': field_type,
                            'value': field_value,
                            'page': 'Document-level',
                            'rect': obj.get('/Rect', []),
                            'flags': obj.get('/Ff', 0)
                        }
                    
                    # Check for nested fields (subforms)
                    if '/Kids' in obj:
                        kids = obj['/Kids']
                        if hasattr(kids, 'get_object'):
                            kids = kids.get_object()
                        
                        for kid in kids:
                            extract_fields_from_object(kid, prefix)
            
            # Check each page for annotations (form fields)
            for page_num, page in enumerate(pdf_reader.pages):
                annotations = page['/Annots']
                if annotations:
                    # Handle IndirectObject references
                    if hasattr(annotations, 'get_object'):
                        annotations = annotations.get_object()
                    
                    for annotation in annotations:
                        if annotation.Subtype == '/Widget':  # Form field
                            field_name = annotation.T
                            if field_name:
                                field_type = annotation.FT if hasattr(annotation, 'FT') else 'Unknown'
                                field_value = annotation.V if hasattr(annotation, 'V') else ''
                                
                                fields_info[field_name] = {
                                    'type': field_type,
                                    'value': field_value,
                                    'page': page_num + 1,
                                    'rect': annotation.Rect if hasattr(annotation, 'Rect') else [],
                                    'flags': annotation.Ff if hasattr(annotation, 'Ff') else 0
                                }
            
            return fields_info
            
        except Exception as e:
            raise Exception(f"Error inspecting PDF form fields: {str(e)}")
    
    @staticmethod
    def inspect_pdf_structure(pdf_file):
        """
        Comprehensive PDF structure inspection
        
        Args:
            pdf_file: PDF file object or path
            
        Returns:
            dict: Detailed PDF structure information
        """
        try:
            pdf_reader = PdfReader(pdf_file)
            
            structure_info = {
                'num_pages': len(pdf_reader.pages),
                'metadata': pdf_reader.Info if hasattr(pdf_reader, 'Info') else {},
                'pages': [],
                'acroform_info': None,
                'document_fields': []
            }
            
            # Inspect each page
            for page_num, page in enumerate(pdf_reader.pages):
                page_info = {
                    'page_num': page_num + 1,
                    'media_box': page.MediaBox if hasattr(page, 'MediaBox') else [],
                    'has_annotations': '/Annots' in page,
                    'fields': []
                }
                
                annotations = page['/Annots']
                if annotations:
                    # Handle IndirectObject references
                    if hasattr(annotations, 'get_object'):
                        annotations = annotations.get_object()
                    
                    for annotation in annotations:
                        if annotation.Subtype == '/Widget':  # Form field
                            field_info = {
                                'name': annotation.T if hasattr(annotation, 'T') else 'Unknown',
                                'type': annotation.FT if hasattr(annotation, 'FT') else 'Unknown',
                                'value': annotation.V if hasattr(annotation, 'V') else '',
                                'rect': annotation.Rect if hasattr(annotation, 'Rect') else [],
                                'flags': annotation.Ff if hasattr(annotation, 'Ff') else 0
                            }
                            page_info['fields'].append(field_info)
                
                structure_info['pages'].append(page_info)
            
            return structure_info
            
        except Exception as e:
            raise Exception(f"Error inspecting PDF structure: {str(e)}")
    
    @staticmethod
    def create_field_mapping(fields_info, mapping_dict=None):
        """
        Create a mapping from readable field names to PDF field names
        
        Args:
            fields_info: Dictionary from inspect_form_fields
            mapping_dict: Optional manual mapping dictionary
            
        Returns:
            dict: Mapping from readable names to PDF field names
        """
        if mapping_dict:
            return mapping_dict
        
        # Default mapping for common W2 fields
        # This is a starting point - you'll need to customize based on your actual PDF
        default_mapping = {
            'employee_name': 'f_01[0]',
            'employee_ssn': 'f_02[0]',
            'employer_name': 'f_03[0]',
            'employer_ein': 'f_04[0]',
            'wages_tips': 'f_05[0]',
            'federal_income_tax': 'f_06[0]',
            'social_security_wages': 'f_07[0]',
            'social_security_tax': 'f_08[0]',
            'medicare_wages': 'f_09[0]',
            'medicare_tax': 'f_10[0]',
            'state_wages': 'f_11[0]',
            'state_income_tax': 'f_12[0]',
            'local_wages': 'f_13[0]',
            'local_income_tax': 'f_14[0]',
        }
        
        # Filter to only include fields that actually exist in the PDF
        actual_mapping = {}
        for readable_name, pdf_field in default_mapping.items():
            if pdf_field in fields_info:
                actual_mapping[readable_name] = pdf_field
        
        return actual_mapping
    
    @staticmethod
    def print_field_analysis(pdf_file):
        """
        Print a detailed analysis of all form fields in a PDF
        
        Args:
            pdf_file: PDF file object or path
        """
        try:
            fields_info = PDFInspector.inspect_form_fields(pdf_file)
            
            print(f"Found {len(fields_info)} form fields:")
            print("=" * 50)
            
            for field_name, info in fields_info.items():
                print(f"Field: {field_name}")
                print(f"  Type: {info['type']}")
                print(f"  Value: {info['value']}")
                print(f"  Page: {info['page']}")
                print("-" * 30)
            
            # Suggest a mapping
            mapping = PDFInspector.create_field_mapping(fields_info)
            print("\nSuggested field mapping:")
            print("=" * 50)
            for readable_name, pdf_field in mapping.items():
                print(f"'{readable_name}': '{pdf_field}',")
                
        except Exception as e:
            print(f"Error analyzing PDF: {str(e)}")
    
    @staticmethod
    def print_comprehensive_analysis(pdf_file):
        """
        Print comprehensive PDF analysis including structure
        
        Args:
            pdf_file: PDF file object or path
        """
        try:
            structure_info = PDFInspector.inspect_pdf_structure(pdf_file)
            
            print(f"PDF Analysis: {pdf_file}")
            print("=" * 60)
            print(f"Number of pages: {structure_info['num_pages']}")
            
            if structure_info['acroform_info']:
                print(f"\nDocument-level AcroForm found:")
                print(f"  Fields: {len(structure_info['acroform_info']['fields'])}")
                print(f"  Need appearances: {structure_info['acroform_info']['need_appearances']}")
                print(f"  Signature flags: {structure_info['acroform_info']['sig_flags']}")
            else:
                print("\nNo document-level AcroForm found")
            
            print(f"\nPage-by-page analysis:")
            print("-" * 40)
            
            total_fields = 0
            for page_info in structure_info['pages']:
                print(f"Page {page_info['page_num']}:")
                print(f"  Has AcroForm: {page_info['has_annotations']}")
                print(f"  Fields: {len(page_info['fields'])}")
                
                if page_info['fields']:
                    print("  Field details:")
                    for field in page_info['fields']:
                        print(f"    - {field['name']} (Type: {field['type']}, Value: '{field['value']}')")
                        total_fields += 1
                
                print()
            
            print(f"Total fields found: {total_fields}")
            
            if total_fields == 0:
                print("\n⚠️  No form fields detected!")
                print("This PDF might:")
                print("  1. Not have fillable form fields")
                print("  2. Use a different form field format")
                print("  3. Be a static PDF that needs text overlay instead")
                print("\nYou may need to:")
                print("  1. Use a different PDF with proper form fields")
                print("  2. Create form fields in the PDF using Adobe Acrobat or similar")
                print("  3. Use text overlay positioning instead of form fields")
                
        except Exception as e:
            print(f"Error analyzing PDF: {str(e)}")


# Command line utility
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pdf_inspector.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    PDFInspector.print_comprehensive_analysis(pdf_path) 