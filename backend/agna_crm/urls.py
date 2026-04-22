from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),  # Auth first
    # path('api/leads/', include('leads.urls')),
    # ... other modules
    
    # API Docs
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema-swagger-ui'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema-redoc'), name='redoc'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    path('api/health/', lambda request: {'status': 'OK'}),  # Healthcheck
]

