from django.core.exceptions import PermissionDenied
from helpdesk.models import Ticket
from helpdesk.views.public import ViewTicket


class SecurePublicTicketView(ViewTicket):
    """Require the per-ticket secret before entering django-helpdesk's view."""

    def get(self, request, *args, **kwargs):
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

        if not Ticket.objects.filter(
            pk=ticket_id,
            submitter_email__iexact=requested_email,
            secret_key__iexact=secret_key,
        ).exists():
            raise PermissionDenied("The secure ticket link is invalid.")

        return super().get(request, *args, **kwargs)
