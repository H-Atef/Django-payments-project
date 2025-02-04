
from payments.helpers.base_payment_gateway import BasePaymentGateway
import stripe
from django.conf import settings
from rest_framework.response import Response
from payments.models import StripePayment
import time


stripe.api_key = settings.STRIPE_SECRET_KEY

class StripePaymentGateway(BasePaymentGateway):
    def create_payment(self, request):
        try:
            email = request.data.get('email')
            amount = request.data.get('amount')
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Payment'},
                        'unit_amount': int(float(amount) * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"http://localhost:8000/payments/stripe/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"http://localhost:8000/payments/stripe/cancel",
                customer_email=email,
            )


            StripePayment.objects.create(
                email=email,
                amount=amount,
                stripe_checkout_session=session.id,
                status='pending'
            )
            return {"status": "success", "checkout_url": session.url}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def payment_success(self, request):
        session_id = request.GET.get('session_id')
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment = StripePayment.objects.get(stripe_checkout_session=session_id)
            payment.stripe_payment_intent = session.payment_intent

            print(session.payment_intent)
            # payment.status = 'completed'
            payment.save()
            payment_summary = {
                "payment_id": payment.id,
                "email": payment.email,
                "amount": str(payment.amount),
                "currency": payment.currency,
                "status": payment.status,
                "transaction_id": payment.stripe_payment_intent, 
                "created_at": payment.created_at,
            }
            return {"status": "success", "payment": payment_summary}
        
        except StripePayment.DoesNotExist:
            return {"status": "error", "message": "Payment not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def payment_cancel(self, request):
        return {"status": "info", "message": "Payment canceled by user"}

    def payment_refund(self, request):
        payment_intent = request.data.get('transaction_id')
        try:
            payment = StripePayment.objects.get(stripe_payment_intent=payment_intent, status='completed')
            refund = stripe.Refund.create(payment_intent=payment_intent)
            
            if refund.status == 'succeeded':
                payment.status = 'refunded'
                payment.save()
                return {"status": "success", "message": "Refund processed"}
            return {"status": "error", "message": "Refund failed"}
        
        except StripePayment.DoesNotExist:
            return {"status": "error", "message": "Payment not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def payment_webhook(self, request):
        try:
            payload = request.body.decode("utf-8")
            sig_header = request.headers.get('Stripe-Signature',None)
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )


            if event['type'] == 'checkout.session.completed':
                session= event["data"]["object"]
                session_id=session["id"] 
                payment_status = session.get("payment_status")
                payment= StripePayment.objects.get(stripe_checkout_session=session_id)
                if payment_status=='paid':
                    payment.status = 'completed'
                    payment.save()
                
            elif event['type'] == 'charge.refunded':
                charge = event['data']['object']
                payment = StripePayment.objects.get(stripe_payment_intent=charge['payment_intent'])
                payment.status = 'refunded'
                payment.save()

            return {"status": "success", "message": "Webhook processed"}
        
        except stripe.error.SignatureVerificationError:
            return {"status": "error", "message": "Invalid signature"}
        except Exception as e:
            print(e)
            return {"status": "error", "message": str(e)}