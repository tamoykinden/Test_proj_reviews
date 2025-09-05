from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Создание router и регистрация  ViewSet
router = DefaultRouter()
router.register(r'countries', views.CountryViewSet, basename='country')
router.register(r'manufactures', views.ManufactureViewSet, basename='manufacture')
router.register(r'cars', views.CarViewSet, basename='car')
router.register(r'comments', views.CommentViewSet, basename='comment')

# URL patterns приложения
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]