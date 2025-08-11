# ============================================================================
# booking_api/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()
router.register(r'cars', views.CarsDetailViewSet)
router.register(r'packages', views.PackageDetailsViewSet)
router.register(r'locations', views.LocationDetailViewSet)
router.register(r'reviews', views.ReviewDetailViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
    path('api/auth/', include('rest_framework.urls')),
]
