from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Product

# Create your views here.
# 一覧表示
class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        queryset = Product.objects.all()

        brand = self.request.GET.get('brand')
        weight = self.request.GET.get('weight')

        if brand:
            queryset = queryset.filter(brand=brand)
        if weight:
            queryset = queryset.filter(weight=weight)

        return queryset

# 詳細ページ
class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
