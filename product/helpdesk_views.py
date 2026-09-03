from functools import wraps
from hashlib import sha256
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from helpdesk.decorators import is_helpdesk_staff
from helpdesk.models import Ticket
from helpdesk.update_ticket import update_ticket
from helpdesk.views.public import (
    BaseCreateTicketView,
    CreateTicketIframeView,
    ViewTicket,
)


def rate_limit_public_ticket_submission(view_func):
    """Apply one fixed-window counter across every public submission route."""

    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if request.method == "POST" and not is_helpdesk_staff(request.user):
            client_address = request.META.get("REMOTE_ADDR", "unknown")
            identity = sha256(client_address.encode()).hexdigest()
            cache_key = f"helpdesk:public-submit:{identity}"
            timeout = settings.HELPDESK_PUBLIC_SUBMISSION_RATE_WINDOW

            if cache.add(cache_key, 1, timeout=timeout):
                attempts = 1
            else:
                try:
                    attempts = cache.incr(cache_key)
                except ValueError:
                    # The fixed-window key can expire between add() and incr().
                    cache.set(cache_key, 1, timeout=timeout)
                    attempts = 1

            if attempts > settings.HELPDESK_PUBLIC_SUBMISSION_RATE_LIMIT:
                response = HttpResponse(
                    "Too many support requests. Please try again later.",
                    status=429,
                )
                response.headers["Retry-After"] = str(timeout)
                return response

        return view_func(request, *args, **kwargs)

    return wrapped


class CsrfProtectedCreateTicketIframeView(CreateTicketIframeView):
    """Keep iframe submission available without bypassing Django's CSRF check."""

    @xframe_options_exempt
    def dispatch(self, request, *args, **kwargs):
        return BaseCreateTicketView.dispatch(self, request, *args, **kwargs)

    def form_valid(self, form):
        response = BaseCreateTicketView.form_valid(self, form)
        if response.status_code == 302:
            return HttpResponseRedirect(reverse("helpdesk:success_iframe"))
        return response


class SecurePublicTicketView(ViewTicket):
    """Require the per-ticket secret before entering django-helpdesk's view."""

    @staticmethod
    def _harden_response(response):
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    def _get_authorized_ticket(self, request):
        ticket_reference = request.GET.get("ticket", "")
        requested_email = request.GET.get("email", "")
        secret_key = request.GET.get("key", "")

        # django-helpdesk's Ticket.ticket_url does not escape plus signs in
        # email addresses, so QueryDict decodes them as spaces. Repair that
        # legacy URL before validating it and before delegating to the package.
        if " " in requested_email:
            requested_email = requested_email.replace(" ", "+")
            query = request.GET.copy()
            query["email"] = requested_email
            request.GET = query

        if not (ticket_reference and requested_email and secret_key):
            raise PermissionDenied("A secure ticket link is required.")

        try:
            _, raw_ticket_id = Ticket.queue_and_id_from_query(ticket_reference)
            ticket_id = int(raw_ticket_id)
            if ticket_id <= 0:
                raise ValueError
        except (TypeError, ValueError) as exc:
            raise PermissionDenied("The secure ticket link is invalid.") from exc

        try:
            return Ticket.objects.get(
                pk=ticket_id,
                submitter_email__iexact=requested_email,
                secret_key__iexact=secret_key,
            )
        except Ticket.DoesNotExist:
            raise PermissionDenied("The secure ticket link is invalid.")

    def get(self, request, *args, **kwargs):
        self._get_authorized_ticket(request)
        if "close" in request.GET:
            return self._harden_response(HttpResponseNotAllowed(["POST"]))
        return self._harden_response(super().get(request, *args, **kwargs))

    def post(self, request, *args, **kwargs):
        ticket = self._get_authorized_ticket(request)
        if request.POST.get("action") != "close":
            return self._harden_response(
                HttpResponseBadRequest("A supported ticket action is required.")
            )

        if ticket.status == Ticket.RESOLVED_STATUS:
            update_ticket(
                request.user,
                ticket,
                public=True,
                comment=_("Submitter accepted resolution and closed ticket"),
                new_status=Ticket.CLOSED_STATUS,
            )

        query = urlencode(
            {
                "ticket": ticket.ticket_for_url,
                "email": ticket.submitter_email,
                "key": ticket.secret_key,
            }
        )
        response = redirect(f"{reverse('helpdesk:public_view')}?{query}")
        return self._harden_response(response)
