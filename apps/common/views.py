from django.http import HttpResponse
from django.template.loader import render_to_string
from apps.catalog.models import Product


def sitemap(request):
    products = Product.active_objects.filter(stock__gt=0).prefetch_related('images')
    xml = render_to_string('sitemap.xml', {'products': products})
    return HttpResponse(xml, content_type='application/xml')


def robots(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /accounts/',
        'Disallow: /cart/',
        'Disallow: /orders/',
        'Disallow: /payments/',
        '',
        'Sitemap: /sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
