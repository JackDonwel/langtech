# payments/flutterwave_utils.py
import requests
import json
from django.conf import settings

class FlutterwaveAPI:
    base_url = "https://api.flutterwave.com/v3"
    
    def __init__(self):
        self.public_key = settings.FLW_PUBLIC_KEY
        self.secret_key = settings.FLW_SECRET_KEY
        self.encryption_key = settings.FLW_ENCRYPTION_KEY
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def initiate_payment(self, data):
        """Initiate a payment transaction"""
        url = f"{self.base_url}/payments"
        payload = {
            "tx_ref": data['tx_ref'],
            "amount": data['amount'],
            "currency": data['currency'],
            "payment_options": "card, mobilemoney, ussd",
            "redirect_url": data['redirect_url'],
            "customer": {
                "email": data['customer_email'],
                "name": data['customer_name']
            },
            "customizations": {
                "title": data.get('title', 'Your Site Name'),
                "description": data.get('description', 'Payment for services'),
                "logo": data.get('logo_url', 'https://yourdomain.com/logo.png')
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()
    
    def verify_transaction(self, transaction_id):
        """Verify a transaction"""
        url = f"{self.base_url}/transactions/{transaction_id}/verify"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_banks(self, country='TZ'):
        """Get list of banks for a country"""
        url = f"{self.base_url}/banks/{country}"
        response = requests.get(url, headers=self.headers)
        return response.json()