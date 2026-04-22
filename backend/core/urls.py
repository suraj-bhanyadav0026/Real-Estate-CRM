from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path
from .views import login_view, me_view, register_view
 
urlpatterns = [
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/me/', me_view, name='me'),
    path('health/', lambda request: {'status': 'healthy'}, name='health'),
    
    # Module 1 - Leads
    path('leads/', lead_list_create, name='lead-list-create'),
    path('leads/<int:pk>/', lead_detail, name='lead-detail'),
    path('leads/<int:pk>/assign/', lead_assign, name='lead-assign'),
    path('leads/<int:pk>/status/', lead_status_update, name='lead-status-update'),
]

