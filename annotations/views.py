from rest_framework import viewsets
from .models import Image, Annotation
from .serializers import ImageSerializer, AnnotationSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientForm, ProcedureForm
from .models import *
from .forms import ImageUploadForm

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

def home(request):
    return render(request,'home.html')

def base(request):
    return render(request,'base.html')

def annotate_image(request):
    return render(request, 'annotate.html')

def patients_view(request):
    all_patients = Patient.objects.all()
    context = {
        'patient': all_patients,
    }
    return render(request, 'patients.html', context)

def patient_details(request, name):
    patient = get_object_or_404(Patient, name=name)
    procedure = patient.procedures.first()
    context = {
        'patient': patient,
        'procedure': procedure,
    }
    return render(request, 'patient_details.html', context)

def edit_patient(request, name):
    patient = get_object_or_404(Patient, name=name)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('patient_manager:patient_details', name=patient.name)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'edit_patient.html', {'form': form})

def delete_patient(request, name):
    patient = get_object_or_404(Patient, name=name)
    if request.method == 'POST':
        patient.delete()
        return redirect('patient_manager:patients')
    return render(request, 'delete_patient.html', {'patient': patient})

def billing_view(request):
    return render(request, 'billing.html')

def reports_view(request):
    return render(request, 'reports.html')

def logout_view(request):
    return render(request, 'logout.html')  



def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_manager:add_procedure')
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form})

def add_procedure(request):
    if request.method == 'POST':
        form = ProcedureForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_manager:home')
    else:
        form = ProcedureForm()
    return render(request, 'add_procedure.html', {'form': form})


def recent_patients(request):
    patients = Patient.objects.all().order_by('-id')[:10]  # Most recent 10
    return render(request, 'recent_patients.html', {'patients': patients})

def upload_image_for_patient(request, name):
    patient = Patient.objects.get(name=name)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.patient = patient
            image.save()
            return redirect('patient_manager:annotate')  # or show confirmation
    else:
        form = ImageUploadForm()
    return render(request, 'upload_image.html', {'form': form, 'patient': patient})