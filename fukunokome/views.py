from django.shortcuts import render
from products.models import Product

def top(request):
    product_list = Product.objects.all().order_by('-is_recommended', '-id')[:6]  # おすすめ順に6件など

    return render(request, 'index.html', {
        'product_list': product_list,
    })
