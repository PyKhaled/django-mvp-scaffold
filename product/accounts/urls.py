from django.urls import path, include
from product.accounts.views import profile, profile_settings, change_password, appearance_settings

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('profile/', profile, name='profile'),
    path('settings/',include(([
        path('profile/', profile_settings, name='profile'),
        path('password/', change_password, name='change_password'),
        path('appearance/', appearance_settings, name='appearance'),
    ],'settings'), namespace='settings')),
]
