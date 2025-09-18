from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_view, name='view_profile'),
    path('edit/<str:target>/', views.edit_profile, name='edit_profile'),
]
