from django.urls import include, path

from product.accounts.views import (
    AccountPasswordChangeView,
    appearance_settings,
    profile,
    profile_settings,
)

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('profile/', profile, name='profile'),
    path('settings/',include(([
        path('profile/', profile_settings, name='profile'),
        path('password/', AccountPasswordChangeView.as_view(), name='change_password'),
        path('appearance/', appearance_settings, name='appearance'),
    ],'settings'), namespace='settings')),
]
