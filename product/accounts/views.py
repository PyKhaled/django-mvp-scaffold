from django.views.generic.edit import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


User = get_user_model()


@login_required
def profile(request):
    return render(request, template_name='profile.html')

@login_required
def profile_settings(request):
    return render(request, template_name='settings/profile.html')

@login_required
def change_password(request):
    return render(request, template_name='settings/password.html')

@login_required
def appearance_settings(request):
    return render(request, template_name='settings/appearance.html')
