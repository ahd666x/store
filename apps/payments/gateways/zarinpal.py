import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from django.conf import settings
from django.urls import reverse


class BaseGateway:
    def pay(self, request, payment):
        raise NotImplementedError

    def verify(self, request, payment):
        raise NotImplementedError


class ZarinpalGateway(BaseGateway):
    def __init__(self):
        self.merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '')
        self.sandbox = getattr(settings, 'ZARINPAL_SANDBOX', True)
        if self.sandbox:
            self.request_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'
            self.verify_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json'
            self.callback_url = 'http://localhost:8000/payments/verify/'
        else:
            self.request_url = 'https://api.zarinpal.com/pg/v4/payment/request.json'
            self.verify_url = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
            self.callback_url = 'https://yourdomain.com/payments/verify/'

    def _post_json(self, url, data):
        req = Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        try:
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            try:
                body = e.read().decode('utf-8')
                return json.loads(body)
            except Exception:
                return {}

    def pay(self, request, payment):
        data = {
            'MerchantID': self.merchant_id,
            'Amount': int(payment.amount),
            'Description': f'پرداخت سفارش #{payment.order.id}',
            'CallbackURL': self.callback_url,
        }
        result = self._post_json(self.request_url, data)
        if result.get('data', {}).get('code') == 100:
            payment.authority = result['data']['authority']
            payment.save()
            return {'success': True, 'url': f'https://sandbox.zarinpal.com/pg/StartPay/{result["data"]["authority"]}'}
        return {'success': False, 'error': result.get('errors', {}).get('message', 'خطا در اتصال به درگاه')}

    def verify(self, request, payment):
        data = {
            'MerchantID': self.merchant_id,
            'Amount': int(payment.amount),
            'Authority': payment.authority,
        }
        result = self._post_json(self.verify_url, data)
        if result.get('data', {}).get('code') in (100, 101):
            return {'success': True, 'ref_id': str(result['data'].get('ref_id', ''))}
        return {'success': False, 'error': result.get('errors', {}).get('message', 'پرداخت ناموفق بود')}
