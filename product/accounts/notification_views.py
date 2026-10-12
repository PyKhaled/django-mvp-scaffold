from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST
from notifications.helpers import invalidate_unread_count_cache
from notifications.utils import slug2id

from product.accounts.models import NotificationPreference
from product.accounts.notification_service import destination


def preview_context(user):
    return {
        "unread_count": user.notifications.unread().count(),
        "header_notifications": user.notifications.all().prefetch_related("actor", "target")[:10],
    }


@login_required
@require_POST
def open_notification(request, slug):
    notice = get_object_or_404(request.user.notifications.all(), pk=slug2id(slug))
    path = destination(notice, request.user)
    notice.mark_as_read()
    invalidate_unread_count_cache(request.user)
    return redirect(path)


@login_required
@require_GET
@never_cache
def preview(request):
    context = preview_context(request.user)
    html = render_to_string("notifications/dropdown_items.html", context, request=request)
    return JsonResponse({"unread_count": context["unread_count"], "html": html})


@login_required
def preferences(request):
    error = None
    if request.method == "POST":
        valid_modes = {value for value, _ in NotificationPreference.EmailMode.choices}
        if any(
            request.POST.get(f"email_{kind}") not in valid_modes
            for kind, _ in NotificationPreference.Kind.choices
        ):
            error = "Choose a valid email delivery option."
        else:
            with transaction.atomic():
                for kind, _ in NotificationPreference.Kind.choices:
                    NotificationPreference.objects.update_or_create(
                        user=request.user,
                        kind=kind,
                        defaults={
                            "in_app": request.POST.get(f"in_app_{kind}") == "on",
                            "email_mode": request.POST[f"email_{kind}"],
                        },
                    )
            messages.success(request, "Your notification preferences were updated.")
            return redirect("settings:notifications")
    saved = {item.kind: item for item in NotificationPreference.objects.filter(user=request.user)}
    rows = [
        (label, saved.get(kind, NotificationPreference(kind=kind)))
        for kind, label in NotificationPreference.Kind.choices
    ]
    return render(
        request,
        "settings/notifications.html",
        {
            "rows": rows,
            "email_modes": NotificationPreference.EmailMode.choices,
            "error": error,
        },
        status=400 if error else 200,
    )
