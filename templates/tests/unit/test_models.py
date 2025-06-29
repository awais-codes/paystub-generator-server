from django.test import TestCase
from templates.models import Template, TemplateInstance

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