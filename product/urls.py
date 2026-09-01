from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

admin.site.site_title = "Product admin"
admin.site.site_header = "Product administration"

sitemaps = {
    "flatpages": FlatPageSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/doc/', include('django.contrib.admindocs.urls')),

    path('hijack/', include('hijack.urls')),

    path('maintenance-mode/', include('maintenance_mode.urls')),

    path("accounts/", include("product.accounts.urls")),

    path("notifications/", include(("notifications.urls", "notifications"))),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

    path('help/', include('helpdesk.urls')),

    path('', TemplateView.as_view(template_name='landing.html')),
    path('', include('django.contrib.flatpages.urls')),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
