import stripe
from django.conf import settings
from django.urls import reverse
from django.http import HttpRequest


class StripeService:
    """Service for handling Stripe payment operations"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    def create_checkout_session(self, template_instance, request: HttpRequest):
        """
        Create a Stripe Checkout session for a template instance
        
        Args:
            template_instance: TemplateInstance object
            request: Django HttpRequest object for building URLs
            
        Returns:
            dict: Stripe checkout session data
        """
        try:
            # Build success and cancel URLs
            success_url = request.build_absolute_uri(
                reverse('template-instance-detail', kwargs={'pk': template_instance.id})
            )
            cancel_url = request.build_absolute_uri(
                reverse('template-instance-detail', kwargs={'pk': template_instance.id})
            )
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f"PDF Document - {template_instance.template.name}",
                            'description': f"Generated PDF from {template_instance.template.name} template",
                        },
                        'unit_amount': 500,  # $5.00 in cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'instance_id': str(template_instance.id),
                    'template_id': str(template_instance.template.id),
                },
            )
            
            # Update template instance with session ID
            template_instance.stripe_session_id = session.id
            template_instance.save()
            
            return {
                'session_id': session.id,
                'checkout_url': session.url,
            }
            
        except Exception as e:
            raise Exception(f"Error creating Stripe checkout session: {str(e)}")
    
    def verify_webhook_signature(self, payload, sig_header, webhook_secret):
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw request body
            sig_header: Stripe signature header
            webhook_secret: Webhook endpoint secret
            
        Returns:
            stripe.Event: Verified Stripe event
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError as e:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise ValueError("Invalid signature")
    
    def handle_payment_success(self, session_id):
        """
        Handle successful payment by updating template instance
        
        Args:
            session_id: Stripe checkout session ID
            
        Returns:
            TemplateInstance: Updated template instance
        """
        from .models import TemplateInstance
        
        try:
            # Get the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Find and update the template instance
                template_instance = TemplateInstance.objects.get(
                    stripe_session_id=session_id
                )
                template_instance.is_paid = True
                template_instance.save()
                
                return template_instance
            else:
                raise Exception("Payment not completed")
                
        except TemplateInstance.DoesNotExist:
            raise Exception("Template instance not found")
        except Exception as e:
            raise Exception(f"Error handling payment success: {str(e)}") 