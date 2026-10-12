def notifications(request):
    if not request.user.is_authenticated:
        return {}
    from product.accounts.notification_views import preview_context

    return preview_context(request.user)
