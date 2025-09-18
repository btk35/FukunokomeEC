from django import forms
from django.contrib import admin
from django.conf import settings
from .models import Product

class ProductAdminForm(forms.ModelForm):
    TAX_RATE_CHOICES = [
        (settings.TAX_RATE_REDUCED, '軽減税率（8%）'),
        (settings.TAX_RATE_STANDARD, '標準税率（10%）'),
    ]

    tax_rate = forms.ChoiceField(
        choices=TAX_RATE_CHOICES,
        label='税率',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Product
        fields = '__all__'


class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm    
    list_display = (
        'name', 'year', 'brand', 'is_milled', 'weight', 'price_per_kg',
        'stock', 'is_recommended', 'is_discounted'
    )
    search_fields = ('name', 'brand', 'year')
    list_filter = ('is_milled', 'is_recommended', 'is_discounted', 'organic_method', 'year')
    list_display_links = ('name', 'brand')

    fieldsets = (
        (None, {
            'fields': (
                'name', 'year', 'brand', 'is_milled', 'weight',
                'description', 'price_per_kg', 'tax_rate', 'stock', 'image'
            ),
            'description': '※ 商品名（Name）空欄時は、銘柄・重さ・精米の有無・産年をもとに自動生成します。<br>生成される商品名の例: "2023年産｜コシヒカリ 精米｜5kg"<br>この商品名は、商品詳細ページやカート内で表示されます。',
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('is_recommended', 'is_discounted', 'organic_method'),
        }),
    )

# 登録
admin.site.register(Product, ProductAdmin)
