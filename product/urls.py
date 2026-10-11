from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from health_check.views import HealthCheckView

from product.views import LandingView

admin.site.site_title = f"{settings.SITE_NAME} admin"
admin.site.site_header = f"{settings.SITE_NAME} administration"
admin.site.index_title = "Administration"

sitemaps = {
    "flatpages": FlatPageSitemap,
}

urlpatterns = [
    path("health/", HealthCheckView.as_view(checks=[
        "health_check.checks.Database", "health_check.checks.Cache",
    ]), name="health_check"),
    path('i18n/', include('django.conf.urls.i18n')),
    
    path('management/admin/', admin.site.urls),
    path('management/admin/doc/', include('django.contrib.admindocs.urls')),
    
    path('', include('user_sessions.urls')),

    path('hijack/', include('hijack.urls')),

    path('maintenance-mode/', include('maintenance_mode.urls')),

    path("accounts/", include("product.accounts.urls")),

    path("notifications/", include(("notifications.urls", "notifications"))),

    path("plans/", include("plans.urls")),

    path("help/", include("product.helpdesk.urls")),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

    path('', LandingView.as_view()),
    path('', include('django.contrib.flatpages.urls')),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
