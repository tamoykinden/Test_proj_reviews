from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'countries', views.CountryViewSet, basename='country')
router.register(r'manufactures', views.ManufactureViewSet, basename='manufacture')
router.register(r'cars', views.CarViewSet, basename='car')
router.register(r'comments', views.CommentViewSet, basename='comment')

# Явные маршруты для экспорта
export_patterns = [
    path('countries/export/', views.CountryViewSet.as_view({'get': 'export'}), name='country-export'),
    path('manufactures/export/', views.ManufactureViewSet.as_view({'get': 'export'}), name='manufacture-export'),
    path('cars/export/', views.CarViewSet.as_view({'get': 'export'}), name='car-export'),
    path('comments/export/', views.CommentViewSet.as_view({'get': 'export'}), name='comment-export'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('', include(export_patterns)),  # Добавляю export маршруты в корень
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
