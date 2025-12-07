from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['quote_request', 'amount', 'currency', 'method', 'reference_number', 'receipt']


class ReceiptUploadForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["receipt"]
        labels = {"receipt": "Upload Receipt"}