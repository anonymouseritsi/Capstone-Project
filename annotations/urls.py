from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, AnnotationViewSet
from .views import annotate_image
from . import views

router = DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'annotations', AnnotationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('annotate/', views.annotate_image, name='annotate'),
]
