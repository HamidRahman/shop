from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
import stripe
from django.conf import settings
from django.urls import reverse
from order.models import Order

# Create Stripe Instance
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:cancelled'))
        #Stripe Checkout Session Data
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'usd',
                    'product_data': {
                        'name':item.product.name,
                    },
                    },
                'quantity': item.quantity,
            })
        #Create Stripe Checkout Session
        session = stripe.checkout.Session.create(**session_data)
        
        return redirect(session.url, code=303)
    else:
        return render(request, 'payment/process.html', locals())
    
def payment_completed(request):
    return render(request, 'payment/completed.html')

def payment_cancelled(request):
    return render(request, 'payment/cancelled.html')