"""Expose django-helpdesk's staff API without its email-owned customer route."""

from helpdesk.views.api import (
    CreateUserView,
    FollowUpAttachmentViewSet,
    FollowUpViewSet,
    TicketViewSet,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="ticket")
router.register("followups", FollowUpViewSet, basename="followups")
router.register("followups-attachments", FollowUpAttachmentViewSet, basename="followupattachments")
router.register("users", CreateUserView, basename="user")

urlpatterns = router.urls
