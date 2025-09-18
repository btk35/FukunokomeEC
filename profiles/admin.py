from django.contrib import admin
from .models import UserProfile, ShippingAddress

admin.site.register(UserProfile)
admin.site.register(ShippingAddress)
