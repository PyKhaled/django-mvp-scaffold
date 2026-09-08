from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from helpdesk.decorators import protect_view

from product.helpdesk_views import SecurePublicTicketView

admin.site.site_title = "Product admin"
admin.site.site_header = "Product administration"
admin.site.index_title = "Administration"

sitemaps = {
    "flatpages": FlatPageSitemap,
}

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    
    path('management/admin/', admin.site.urls),
    path('management/admin/doc/', include('django.contrib.admindocs.urls')),
    
    path('hijack/', include('hijack.urls')),

    path('maintenance-mode/', include('maintenance_mode.urls')),

    path("accounts/", include("product.accounts.urls")),

    path("notifications/", include(("notifications.urls", "notifications"))),

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),

    # This route must precede django-helpdesk's URL include so blank legacy
    # secret keys cannot bypass anonymous ticket authorization.
    path('help/view/', protect_view(SecurePublicTicketView.as_view())),
    path('help/', include('product.helpdesk_urls')),

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
