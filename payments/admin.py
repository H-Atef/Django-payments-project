from django.contrib import admin
from . import models 

admin.site.register(models.PayPalPayment)
admin.site.register(models.StripePayment)
