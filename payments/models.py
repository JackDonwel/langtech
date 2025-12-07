from django.db import models
from django.utils import timezone
from lessons.models import Course
from quotes.models import QuoteRequest 
from django.conf import settings
from bookings.models import Booking
from django.contrib.auth import get_user_model
from django.conf import settings

# from .currency import Currency      # removed, Currency is defined below
# from .payment_method import PaymentMethod

class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)   # e.g. USD, TZS
    symbol = models.CharField(max_length=10)              # $, TSh
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} ({self.symbol})"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. M-Pesa, PayPal
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name




class Payment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.ForeignKey("bookings.Booking", null=True, blank=True, on_delete=models.SET_NULL)
    quote_request = models.ForeignKey("quotes.QuoteRequest", null=True, blank=True, on_delete=models.SET_NULL)
    video = models.ForeignKey("content.Video", null=True, blank=True, on_delete=models.SET_NULL)
    course = models.ForeignKey("lessons.Course", null=True, blank=True, on_delete=models.SET_NULL)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.ForeignKey("payments.Currency", on_delete=models.PROTECT)
    method = models.ForeignKey("payments.PaymentMethod", on_delete=models.PROTECT)
    reference_number = models.CharField(max_length=100, unique=True)

    # ✅ New fields
    receipt = models.ImageField(upload_to="receipts/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    is_confirmed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.reference_number} ({self.status})"
    
class PaymentTransaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    provider_reference = models.CharField(max_length=100)  # e.g. M-Pesa code, PayPal txn ID
    provider_status = models.CharField(max_length=50)      # e.g. SUCCESS, FAILED
    provider_response = models.TextField()                 # full JSON or text response (optional)
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider_reference} ({self.provider_status})"

class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    refunded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class FlutterwaveTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    tx_ref = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    flw_transaction_id = models.BigIntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_type = models.CharField(max_length=50, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tx_ref} - {self.amount}"