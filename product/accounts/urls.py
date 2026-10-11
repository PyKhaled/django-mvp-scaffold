from django.contrib.auth.views import LoginView
from django.urls import include, path

from product.accounts.rate_limits import authentication_rate_limit
from product.accounts.views import (
    AccountPasswordChangeView,
    AccountPasswordResetView,
    appearance_settings,
    profile,
    profile_settings,
)

urlpatterns = [
    path('login/', authentication_rate_limit(LoginView.as_view()), name='login'),
    path('password_reset/', authentication_rate_limit(AccountPasswordResetView.as_view()), name='password_reset'),
    path('', include('django.contrib.auth.urls')),
    path('profile/', profile, name='profile'),
    path('settings/',include(([
        path('profile/', profile_settings, name='profile'),
        path('password/', AccountPasswordChangeView.as_view(), name='change_password'),
        path('appearance/', appearance_settings, name='appearance'),
    ],'settings'), namespace='settings')),
]
