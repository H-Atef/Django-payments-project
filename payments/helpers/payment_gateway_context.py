

from payments.helpers.paypal_payment_gateway import PayPalPaymentGateway
from payments.helpers.base_payment_gateway import BasePaymentGateway
from payments.helpers.stripe_payment_gateway import StripePaymentGateway

class PaymentGatewayContext:

    def __init__(self,payment_method="paypal"):
        self.payment_gateways={
            "paypal":PayPalPaymentGateway(),
            "stripe":StripePaymentGateway()
        }
        self.payment_method=payment_method
        self.payment_gateway:BasePaymentGateway=None

    def initialize_payment_gateway(self,payment_method:str=None):
        if not payment_method:
            self.payment_gateway=self.payment_gateways[self.payment_method]
            return self.payment_gateway
        else:
            self.payment_gateway=self.payment_gateways[payment_method]
            return self.payment_gateway
        

     
    def create_payment(self,request):
        if self.payment_gateway:
            return self.payment_gateway.create_payment(request)
        else:
            return {"error":"Payment Gateway Not Initialized"}

   
    def payment_success(self,request):
        if self.payment_gateway:
            return self.payment_gateway.payment_success(request)
        else:
                return {"error":"Payment Gateway Not Initialized"}
    
    def payment_cancel(self,request):
        if self.payment_gateway:
            return self.payment_gateway.payment_cancel(request)
        else:
                return {"error":"Payment Gateway Not Initialized"}
   
    def payment_refund(self,request):
        if self.payment_gateway:
             return self.payment_gateway.payment_refund(request)
        else:
                return {"error":"Payment Gateway Not Initialized"}
   
    def payment_webhook(self,request):
        if self.payment_gateway:
             return self.payment_gateway.payment_webhook(request)
        else:
                return {"error":"Payment Gateway Not Initialized"}
