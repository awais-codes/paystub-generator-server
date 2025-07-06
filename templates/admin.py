from django.contrib import admin
from .models import Template, TemplateInstance, TemplatePreview

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'price', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_editable = ['is_active', 'price']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'template_type', 'description')
        }),
        ('Template File', {
            'fields': ('file', 'preview_file')
        }),
        ('Settings', {
            'fields': ('is_active', 'price')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TemplateInstance)
class TemplateInstanceAdmin(admin.ModelAdmin):
    list_display = ['template', 'is_paid', 'created_at']
    list_filter = ['template__template_type', 'is_paid', 'created_at']
    search_fields = ['template__name', 'stripe_session_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Instance Information', {
            'fields': ('id', 'template', 'data')
        }),
        ('Generated File', {
            'fields': ('file',)
        }),
        ('Payment', {
            'fields': ('is_paid', 'stripe_session_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TemplatePreview)
class TemplatePreviewAdmin(admin.ModelAdmin):
    list_display = ['template', 'created_at', 'updated_at']
    list_filter = ['template__template_type', 'created_at']
    search_fields = ['template__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Preview Information', {
            'fields': ('id', 'template', 'data')
        }),
        ('Generated Preview File', {
            'fields': ('file',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )