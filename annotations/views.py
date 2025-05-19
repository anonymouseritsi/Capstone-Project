from rest_framework import viewsets
from .models import Image, Annotation
from .serializers import ImageSerializer, AnnotationSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientForm, ProcedureForm
from .models import *
from .forms import ImageUploadForm
import base64
from django.core.files.base import ContentFile

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.all()
    serializer_class = AnnotationSerializer

def home(request):
    patients = Patient.objects.all().order_by('-created_at')
    context = {
        'patients': patients
    }
    return render(request,'home.html', context)

def base(request):
    return render(request,'base.html')

def annotate_image(request):
    return render(request, 'annotate.html')

def patients_view(request):
    all_patients = Patient.objects.all().order_by('-created_at')
    context = {
        'patient': all_patients,
    }
    return render(request, 'patients.html', context)

def patient_details(request, name):
    patient = get_object_or_404(Patient, name=name)
    procedure = patient.procedures.first()
    #bagong dagdag
    total_cost = patient.total_procedure_cost()
    context = {
        'patient': patient,
        'procedure': procedure,
<<<<<<< HEAD
        'Procedure': Procedure,
=======
        #bagong dagdag
        'total_cost': total_cost,
>>>>>>> e8a00795b0d8f3b24825f2534005e07a4f03b36b
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
    patients = Patient.objects.all().order_by('-created_at')[:10]  # Most recent 10
    return render(request, 'recent_patients.html', {'patients': patients})

def upload_image_for_patient(request, name):
    patient = Patient.objects.get(name=name)
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.patient = patient
            image.save()
            return redirect('patient_manager:annotate', name=patient.name)  # or show confirmation
    else:
        form = ImageUploadForm()
    return render(request, 'upload_image.html', {'form': form, 'patient': patient})


def save_annotation(request, name):
    if request.method == 'POST':
        patient = get_object_or_404(Patient, name=name)
        data_url = request.POST.get('imageData')

        if data_url:
            format, imgstr = data_url.split(';base64,') 
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name=f'annotated_{patient.name}.{ext}')

            latest_image = patient.images.last()
            if latest_image:
                latest_image.annotated_image.save(data.name, data)
                latest_image.save()

        return redirect('patient_manager:patient_details', name=patient.name)
from docx import Document
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import requests
from tempfile import NamedTemporaryFile
from .models import Patient  # Ensure this import matches your app's structure

def download_patient_details(request, name):
    patient = get_object_or_404(Patient, name=name)
    procedure = patient.procedures.first()

    document = Document()
    document.add_heading('Patient Details', 0)

    paragraph = document.add_paragraph()
    paragraph.add_run(f"Name: {patient.name}")
    paragraph.add_run(f"\nAge: {patient.age}")

    document.add_heading('Procedures', 1)
    if procedure:
        paragraph = document.add_paragraph()
        paragraph.add_run(f"Procedure: {procedure.procedure_type}")
        paragraph.add_run(f"\nDate: {procedure.date}")
        paragraph.add_run(f"\nNotes: {procedure.notes}")
    else:
        document.add_paragraph("No procedure information available.")

    document.add_heading('Images', 1)
    for image in patient.images.all():
        paragraph = document.add_paragraph()
        paragraph.add_run(f"Image {image.id}:")

        # Original Image
        try:
            original_url = request.build_absolute_uri(image.image.url)
            img_response = requests.get(original_url)
            img_response.raise_for_status()

            with NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                tmp.write(img_response.content)
                tmp.flush()
                document.add_paragraph("Original Image:")
                document.add_picture(tmp.name, width=None)
        except requests.RequestException as e:
            document.add_paragraph(f"(Original image could not be loaded: {e})")

        # Annotated Image (if available)
        if image.annotated_image:
            try:
                annotated_url = request.build_absolute_uri(image.annotated_image.url)
                ann_response = requests.get(annotated_url)
                ann_response.raise_for_status()

                with NamedTemporaryFile(suffix='.jpg', delete=False) as ann_tmp:
                    ann_tmp.write(ann_response.content)
                    ann_tmp.flush()
                    document.add_paragraph("Annotated Image:")
                    document.add_picture(ann_tmp.name, width=None)
            except requests.RequestException as e:
                document.add_paragraph(f"(Annotated image could not be loaded: {e})")

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename={patient.name}_details.docx'
    document.save(response)

    return response



def annotate_image(request, name):
    patient = get_object_or_404(Patient, name=name)
    return render(request, 'annotate.html', {'patient': patient})

