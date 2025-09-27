"""
URL configuration for hotspot_config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/billing-templates/', include('billing_templates.urls')),

    # Multi-level platform URLs
    path('super-admin/', include('super_admin.urls')),
    path('provider/', include('provider.urls')),
    path('cashier/', include('cashier.urls')),
    path('portal/', include('captive_portal.urls')),

    # Original URLs
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('dashboard/tickets/', include('tickets.urls')),
    path('dashboard/reports/', include('reports.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
