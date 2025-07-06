"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from templates.views import TemplateViewSet, TemplateInstanceViewSet, StripeWebhookView, TemplatePreviewViewSet


router = DefaultRouter()
router.register(r'templates', TemplateViewSet, basename='template')
router.register(r'template-instances', TemplateInstanceViewSet, basename='template-instance')
router.register(r'template-previews', TemplatePreviewViewSet, basename='template-preview')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]
