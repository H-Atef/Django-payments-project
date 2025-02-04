from django.urls import path
from . import views

urlpatterns = [
    path('<str:payment_method>/create/', views.CreatePaymentView.as_view(), name='create_payment'),
    path('<str:payment_method>/success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('<str:payment_method>/cancel/', views.PaymentCancelView.as_view(), name='payment_cancel'),
    path('<str:payment_method>/refund/', views.RefundPaymentView.as_view(), name='payment_refund'),
    path('<str:payment_method>/webhook/', views.PaymentGatewayWebhookView.as_view(), name='payment_gateway_webhook'),
]
