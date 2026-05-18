import requests
from django.conf import settings
from django.shortcuts import redirect,render

def create_payment(request):

    url = "https://api.moyasar.com/v1/invoices"

    payload = {
        "amount": 4900,
        "currency": "SAR",
        "description": "اشتراك إحتواء برو",
        "callback_url": "https://spooky-darkish-underwent.ngrok-free.dev/payments/success/"
    }

    response = requests.post(
        url,
        json=payload,
        auth=(settings.MOYASAR_SECRET_KEY, '')
    )

    data = response.json()

    print(data)

    return redirect(data["url"])

def payment_success(request):
    return render(request, 'payments/success.html')