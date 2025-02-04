from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from payments.helpers.payment_gateway_context import PaymentGatewayContext  # Import context



class CreatePaymentView(APIView):
    """
    Handles payment creation and returns an approval URL for the user to complete the payment.
    """
    def post(self, request, payment_method):
        gateway_context = PaymentGatewayContext(payment_method)
        gateway_context.initialize_payment_gateway()

        response = gateway_context.create_payment(request)
        return Response(response, status=status.HTTP_200_OK if "error" not in response else status.HTTP_400_BAD_REQUEST)


class PaymentSuccessView(APIView):
    """
    Handles successful payments.
    """
    def get(self, request, payment_method):
        gateway_context = PaymentGatewayContext(payment_method)
        gateway_context.initialize_payment_gateway()

        response = gateway_context.payment_success(request)
        return Response(response, status=status.HTTP_200_OK)


class PaymentCancelView(APIView):
    """
    Handles canceled payments.
    """
    def get(self, request, payment_method):
        gateway_context = PaymentGatewayContext(payment_method)
        gateway_context.initialize_payment_gateway()

        response = gateway_context.payment_cancel(request)
        return Response(response, status=status.HTTP_200_OK)


class RefundPaymentView(APIView):
    """
    Handles payment refunds.
    """
    def post(self, request, payment_method):
        gateway_context = PaymentGatewayContext(payment_method)
        gateway_context.initialize_payment_gateway()

        response = gateway_context.payment_refund(request)
        return Response(response, status=status.HTTP_200_OK if "error" not in response else status.HTTP_400_BAD_REQUEST)


class PaymentGatewayWebhookView(APIView):
    """
    Handles webhooks to update payment statuses.
    """
    def post(self, request, payment_method):
        gateway_context = PaymentGatewayContext(payment_method)
        gateway_context.initialize_payment_gateway()
        response = gateway_context.payment_webhook(request)
        return Response(response, status=status.HTTP_200_OK if "error" not in response else status.HTTP_400_BAD_REQUEST)
