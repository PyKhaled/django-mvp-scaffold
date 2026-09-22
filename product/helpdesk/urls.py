"""Expose and secure django-helpdesk routes."""

from django.urls import include, path

from helpdesk.decorators import protect_view
from helpdesk.urls import urlpatterns as upstream_urlpatterns
from helpdesk.views.public import Homepage, create_ticket

from product.helpdesk_views import (CsrfProtectedCreateTicketIframeView, SecurePublicTicketView,rate_limit_public_ticket_submission)


app_name = "helpdesk"


# Routes overridden by this project.
EXCLUDED_UPSTREAM_URL_NAMES = {
    "home",
    "my-tickets",
    "submit",
    "submit_iframe",
}


# Keep all django-helpdesk routes except those explicitly overridden.
upstream_patterns = [
    pattern
    for pattern in upstream_urlpatterns
    if getattr(pattern, "name", None) not in EXCLUDED_UPSTREAM_URL_NAMES
]


urlpatterns = [
    # Must precede django-helpdesk's upstream routes so blank legacy
    # secret keys cannot bypass anonymous ticket authorization.
    path("view/", protect_view(SecurePublicTicketView.as_view()), name="view"),

    # Secure public ticket submission.
    path("tickets/submit/", rate_limit_public_ticket_submission(create_ticket), name="submit"),

    # Secure iframe ticket submission.
    path("tickets/submit_iframe/", rate_limit_public_ticket_submission(protect_view(CsrfProtectedCreateTicketIframeView.as_view())), name="submit_iframe"),

    # Project-specific Helpdesk API.
    path("api/", include("product.helpdesk_api_urls"),),

    # Helpdesk homepage.
    path("", protect_view(rate_limit_public_ticket_submission(Homepage.as_view())), name="home"),

    # Everything else from django-helpdesk.
    *upstream_patterns,
]