from django.urls import include, path

from .invoice import urls as invoice_urls
from .order import urls as order_urls
from .payment import urls as payment_urls
from .quote import urls as quote_urls

internal_frontend_urls = [
    path('', include((order_urls.internal_frontend_urls, 'order'), namespace='order')),
    path('', include((quote_urls.internal_frontend_urls, 'quote'), namespace='quote')),
    path('', include((invoice_urls.internal_frontend_urls, 'invoice'), namespace='invoice')),
    path('', include((payment_urls.internal_frontend_urls, 'payment'), namespace='payment')),
]

public_urls = [
    path('', include((order_urls.public_urls, 'order'), namespace='order')),
    path('', include((quote_urls.public_urls, 'quote'), namespace='quote')),
    path('', include((invoice_urls.public_urls, 'invoice'), namespace='invoice')),
    path('', include((payment_urls.public_urls, 'payment'), namespace='payment')),
]
