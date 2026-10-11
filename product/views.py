from django.conf import settings
from django.views.generic import TemplateView
from meta.views import Meta


class LandingView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["meta"] = Meta(
            title=f"{settings.SITE_NAME} · Accounts and support",
            description=f"{settings.SITE_NAME} provides accounts, profile settings, notifications, and support.",
            url="/", use_og=True, use_twitter=True, use_title_tag=True,
        )
        return context
