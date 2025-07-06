from django.test import TestCase
from templates.models import Template, TemplateInstance, TemplatePreview
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class TemplateModelTest(TestCase):
    def test_str(self):
        t = Template.objects.create(name="Test Template")
        self.assertEqual(str(t), "Other - Test Template")
    
    def test_str_with_template_type(self):
        t = Template.objects.create(name="Test Paystub", template_type="paystub")
        self.assertEqual(str(t), "Paystub - Test Paystub")

class TemplateInstanceModelTest(TestCase):
    def test_str(self):
        t = Template.objects.create(name="Test Template")
        inst = TemplateInstance.objects.create(template=t, data={"foo": "bar"})
        self.assertIn("Test Template", str(inst))

class TemplatePreviewModelTest(TestCase):
    def setUp(self):
        pdf_path = os.path.join(os.path.dirname(__file__), '../fixtures/test_files/w2_template.pdf')
        with open(os.path.abspath(pdf_path), 'rb') as f:
            pdf_bytes = f.read()
        self.main_pdf = SimpleUploadedFile("main.pdf", pdf_bytes, content_type="application/pdf")
        self.preview_pdf = SimpleUploadedFile("preview.pdf", pdf_bytes, content_type="application/pdf")
        self.template = Template.objects.create(
            name="Preview Model Template",
            template_type="w2",
            file=self.main_pdf,
            preview_file=self.preview_pdf,
            is_active=True,
            price=10.00
        )
    def test_create_preview(self):
        preview = TemplatePreview.objects.create(template=self.template, data={"foo": "bar"})
        self.assertEqual(preview.template, self.template)
        self.assertEqual(preview.data["foo"], "bar")
    def test_str(self):
        preview = TemplatePreview.objects.create(template=self.template, data={"foo": "bar"})
        self.assertIn("Preview of", str(preview))
        self.assertIn(self.template.name, str(preview))
    def test_related_name(self):
        preview = TemplatePreview.objects.create(template=self.template, data={"foo": "bar"})
        self.assertIn(preview, self.template.previews.all()) 