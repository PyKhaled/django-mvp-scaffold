"""Expose django-helpdesk without its unsafe email-owned ticket listing."""

from django.urls import include, path
from helpdesk.decorators import protect_view
from helpdesk.urls import urlpatterns as upstream_urlpatterns
from helpdesk.views.public import Homepage, create_ticket

from product.helpdesk_views import (
    CsrfProtectedCreateTicketIframeView,
    rate_limit_public_ticket_submission,
)

app_name = "helpdesk"

urlpatterns = [
    pattern
    for pattern in upstream_urlpatterns
    if getattr(pattern, "name", None)
    not in {"home", "my-tickets", "submit", "submit_iframe"}
]

urlpatterns.extend(
    [
        path(
            "tickets/submit/",
            rate_limit_public_ticket_submission(create_ticket),
            name="submit",
        ),
        path(
            "tickets/submit_iframe/",
            rate_limit_public_ticket_submission(
                protect_view(CsrfProtectedCreateTicketIframeView.as_view())
            ),
            name="submit_iframe",
        ),
        path(
            "api/",
            include("product.helpdesk_api_urls"),
        ),
        path(
            "",
            protect_view(rate_limit_public_ticket_submission(Homepage.as_view())),
            name="home",
        ),
    ]
)
