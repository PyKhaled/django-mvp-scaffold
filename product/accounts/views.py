from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, render

from product.accounts.forms import ProfileForm


User = get_user_model()


@login_required
def profile(request):
    return render(request, template_name='profile.html')

@login_required
def profile_settings(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was updated.")
            return redirect("settings:profile")
    else:
        form = ProfileForm(instance=request.user)

    return render(request, template_name='settings/profile.html', context={"form": form})


class AccountPasswordChangeView(PasswordChangeView):
    template_name = "settings/password.html"
    success_url = reverse_lazy("settings:change_password")

    def form_valid(self, form):
        messages.success(self.request, "Your password was changed.")
        return super().form_valid(form)

@login_required
def appearance_settings(request):
    return render(request, template_name='settings/appearance.html')
