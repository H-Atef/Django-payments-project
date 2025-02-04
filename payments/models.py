
from django.db import models
import datetime

class StripePayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    email = models.EmailField()  # Customer email
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Payment amount
    currency = models.CharField(max_length=10, default="USD")  # Currency
    stripe_payment_intent = models.CharField(max_length=255, unique=True, blank=True, null=True)  # Stripe PaymentIntent ID
    stripe_checkout_session = models.CharField(max_length=255, unique=True, blank=True, null=True)  # Stripe Checkout Session ID
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")  # Payment status
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.id} - {self.email} - {self.amount} {self.currency}"


    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = datetime.datetime.now()
        super().save(*args, **kwargs)




class PayPalPayment(models.Model):
    STATUS_CHOICES = (
        ('created', 'Created'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
    )

    email = models.EmailField() 
    payment_email = models.EmailField(null=True, blank=True) 
    paypal_payment_id = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.paypal_payment_id} - {self.status}"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = datetime.datetime.now()
        super().save(*args, **kwargs)