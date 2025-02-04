
from payments.helpers.base_payment_gateway import BasePaymentGateway
from django.conf import settings
from payments.models import PayPalPayment
import requests
import paypalrestsdk


# Configure SDKs
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})



class PayPalPaymentGateway(BasePaymentGateway):
    def create_payment(self, request):
        try:
            email = request.data.get('email')
            amount = request.data.get('amount')

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {"total": f"{amount}", "currency": "USD"},
                    "payee": {"email": settings.PAYPAL_RECEIVER_EMAIL},
                    "description": "Payment description"
                }],
                "redirect_urls": {
                    "return_url": f"http://localhost:8000/payments/paypal/success",
                    "cancel_url": f"http://localhost:8000/payments/paypal/cancel"
                }
            })

            if payment.create():
                PayPalPayment.objects.create(
                    email=email,
                    paypal_payment_id=payment.id,
                    amount=amount,
                    status='created'
                )
                return {"status": "success", "approval_url": next(link.href for link in payment.links if link.rel == "approval_url")}
            return {"status": "error", "message": payment.error}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def payment_success(self, request):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        
        try:
            payment = PayPalPayment.objects.get(paypal_payment_id=payment_id)
            pp_payment = paypalrestsdk.Payment.find(payment_id)
            
            if pp_payment.execute({"payer_id": payer_id}):
                #payment.status = 'completed'
                payment.payment_email = pp_payment.payer.payer_info.email
                payment.save()
                payment_summary = {
                    "payment_id": payment.paypal_payment_id,
                    "payment_email": payment.payment_email,
                    "email": payment.email,
                    "amount": str(payment.amount),
                    "currency": "USD",
                    "status": payment.status,
                    "created_at": payment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "payer_id": payer_id,
                }
                return {"status": "success", "payment": payment_summary}
            return {"status": "error", "message": "Payment execution failed"}
        
        except PayPalPayment.DoesNotExist:
            return {"status": "error", "message": "Payment not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def payment_cancel(self, request):
        return {"status": "info", "message": "Payment canceled by user"}

    def payment_refund(self, request):
        transaction_id = request.data.get('transaction_id')
        try:
            payment = PayPalPayment.objects.get(transaction_id=transaction_id, status='completed')
            sale = paypalrestsdk.Sale.find(transaction_id)
            refund = sale.refund({"amount": {"total": str(payment.amount), "currency": "USD"}})
            
            if refund.success():
                payment.status = 'refunded'
                payment.save()
                return {"status": "success", "message": "Refund processed"}
            return {"status": "error", "message": refund.error}
        
        except PayPalPayment.DoesNotExist:
            return {"status": "error", "message": "Payment not found"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def payment_webhook(self, request):
        try:
            webhook_event = request.data
            event_type = webhook_event.get("event_type")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._get_paypal_access_token()}",
            }
            verification_payload = {
                "auth_algo": request.headers.get("PAYPAL-AUTH-ALGO"),
                "cert_url": request.headers.get("PAYPAL-CERT-URL"),
                "transmission_id": request.headers.get("PAYPAL-TRANSMISSION-ID"),
                "transmission_sig": request.headers.get("PAYPAL-TRANSMISSION-SIG"),
                "transmission_time": request.headers.get("PAYPAL-TRANSMISSION-TIME"),
                "webhook_id": settings.PAYPAL_WEBHOOK_ID,
                "webhook_event": webhook_event,
            }
            verify_response = requests.post("https://api.sandbox.paypal.com/v1/notifications/verify-webhook-signature", json=verification_payload, headers=headers)
            verify_status = verify_response.json().get("verification_status")

            if verify_status != "SUCCESS":
                return {"error": "Invalid webhook signature."}

            if event_type == "PAYMENT.SALE.COMPLETED":
                sale_id = webhook_event["resource"]["id"]
                payment_id = webhook_event["resource"].get("parent_payment")
                transaction = PayPalPayment.objects.filter(paypal_payment_id=payment_id).first()
                if transaction:
                    transaction.transaction_id = sale_id
                    transaction.status = "completed"
                    transaction.save()

            elif event_type == "PAYMENT.SALE.DENIED":
                sale_id = webhook_event["resource"]["id"]
                payment_id = webhook_event["resource"].get("parent_payment")
                transaction = PayPalPayment.objects.filter(paypal_payment_id=payment_id).first()
                if transaction:
                    transaction.status = "declined"
                    transaction.save()

            elif event_type == "PAYMENT.SALE.REFUNDED":
                sale_id = webhook_event["resource"]["sale_id"]
                transaction = PayPalPayment.objects.filter(transaction_id=sale_id).first()
                if transaction:
                    transaction.status = "refunded"
                    transaction.save()

            return {"message": "Webhook received."}
        except Exception as e:
            return {"error": str(e)}
        
    def _get_paypal_access_token(self):
        """Fetch PayPal Access Token"""
        response = requests.post(
            "https://api-m.sandbox.paypal.com/v1/oauth2/token",
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET ),
            data={"grant_type": "client_credentials"},
        )
        return response.json().get("access_token")

