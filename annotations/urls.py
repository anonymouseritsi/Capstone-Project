from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet, AnnotationViewSet
from .views import annotate_image, home, patients_view, billing_view, reports_view, logout_view,masters,add_patient,add_procedure,recent_patients,upload_image_for_patient

router = DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'annotations', AnnotationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', home, name='home'),
    path('', masters, name='masters'),
    path('annotate/', annotate_image, name='annotate'),
    path('patients/', patients_view, name='patients'),
    path('billing/', billing_view, name='billing'),
    path('reports/', reports_view, name='reports'),
    path('logout/', logout_view, name='logout'),
    path('add-patient/', add_patient, name='add_patient'),
    path('add-procedure/', add_procedure, name='add_procedure'),
    path('recent-patients/', recent_patients, name='recent_patients'),
    path('patient/<int:patient_id>/upload-image/', upload_image_for_patient, name='upload_image'),
]
