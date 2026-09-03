from .models import ProductCategory

def categories_menu(request):
    return {'nav_categories': ProductCategory.objects.all()}
