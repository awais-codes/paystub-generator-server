from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Template, TemplateInstance
from .serializers import TemplateSerializer, TemplateInstanceSerializer

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    parser_classes = (MultiPartParser, FormParser)

class TemplateInstanceViewSet(viewsets.ModelViewSet):
    queryset = TemplateInstance.objects.all()
    serializer_class = TemplateInstanceSerializer