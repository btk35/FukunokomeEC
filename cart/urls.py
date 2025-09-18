from . import views
from django.urls import path

app_name = 'cart'

urlpatterns = [
    path('', views.cart_view, name='view_cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('update/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('badge/', views.badge_partial, name='badge'),
]
