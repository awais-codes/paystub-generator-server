from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from ..services.stripe_service import StripeService

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """Handle Stripe webhooks for payment confirmation"""
    
    def post(self, request, *args, **kwargs):
        try:
            # Get the webhook payload and signature
            payload = request.body
            sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
            
            if not sig_header:
                return HttpResponse('Missing signature', status=400)
            
            # Verify webhook signature
            stripe_service = StripeService()
            event = stripe_service.verify_webhook_signature(
                payload, sig_header, stripe_service.webhook_secret
            )
            
            # Handle the event
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                template_instance = stripe_service.handle_payment_success(session['id'])
                
                return HttpResponse('Payment processed successfully', status=200)
            
            return HttpResponse('Event ignored', status=200)
            
        except ValueError as e:
            return HttpResponse(f'Invalid payload: {str(e)}', status=400)
        except Exception as e:
            return HttpResponse(f'Error processing webhook: {str(e)}', status=500)