from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, AnnotationViewSet
from .views import *
from . import views

router = DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'annotations', AnnotationViewSet)

app_name = 'patient_manager'

urlpatterns = [
    path('api/', include(router.urls)),
    # path('', base, name='base')
    path('home/', views.home, name='home'),
    path('', base, name='base'),
    path('annotate/', annotate_image, name='annotate'),
    path('patients/', patients_view, name='patients'),
    path('patients/<str:name>/', views.patient_details, name='patient_details'),
    path('patients/<str:name>/edit/', edit_patient, name='edit_patient'),
    path('patients/<str:name>/delete/', delete_patient, name='delete_patient'),
    path('billing/', billing_view, name='billing'),
    path('reports/', reports_view, name='reports'),
    path('logout/', logout_view, name='logout'),
    path('add-patient/', add_patient, name='add_patient'),
    path('add-procedure/', add_procedure, name='add_procedure'),
    path('recent-patients/', recent_patients, name='recent_patients'),
    path('patient/<str:name>/upload-image/', upload_image_for_patient, name='upload_image'),
    path('patient/<str:name>/download_details/', views.download_patient_details, name='download_patient_details'),
    path('annotate/<str:name>/', views.annotate_image, name='annotate_image'),
]
