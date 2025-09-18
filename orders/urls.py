from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('detail/', views.order_detail_view, name='order_detail'),
    path("confirm/", views.order_confirm_view, name="order_confirm"),
    path("complete/", views.order_complete_view, name="order_complete"),
    path('history/', views.order_history, name='order_history'),
]
