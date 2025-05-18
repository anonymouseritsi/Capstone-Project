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
    all_patients = Patient.objects.all().order_by('-created_at')
    context = {
        'patient': all_patients,
    }
    return render(request,'home.html', context)

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

# from docx import Document
# from django.http import HttpResponse

# def download_patient_details(request, name):
#     patient = get_object_or_404(Patient, name=name)
#     procedure = patient.procedures.first()

#     document = Document()
#     document.add_heading('Patient Details', 0)

#     paragraph = document.add_paragraph()
#     paragraph.add_run(f"Name: {patient.name}")
#     paragraph.add_run(f"\nAge: {patient.age}")

#     document.add_heading('Procedures', 1)
#     paragraph = document.add_paragraph()
#     paragraph.add_run(f"Procedure: {procedure.procedure_type}")
#     paragraph.add_run(f"\nDate: {procedure.date}")
#     paragraph.add_run(f"\nNotes: {procedure.notes}")

#     document.add_heading('Images', 1)
#     for image in patient.images.all():
#         paragraph = document.add_paragraph()
#         paragraph.add_run(f"Image {image.id}: {image.image.url}")

#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
#     response['Content-Disposition'] = f'attachment; filename={patient.name}_details.docx'
#     document.save(response)

#     return response

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

        # Fix: Use absolute URL
        relative_url = image.image.url  # e.g. '/media/uploads/image.jpg'
        full_url = request.build_absolute_uri(relative_url)

        try:
            img_response = requests.get(full_url)
            img_response.raise_for_status()
        except requests.RequestException as e:
            paragraph.add_run(f" (Image could not be loaded: {e})")
            continue

        with NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(img_response.content)
            tmp.flush()
            try:
                document.add_picture(tmp.name, width=None)
            except Exception as e:
                paragraph.add_run(f" (Failed to insert image: {e})")

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename={patient.name}_details.docx'
    document.save(response)

    return response

# def annotate_image(request):
#     patient = get_object_or_404(Patient, name=request.GET.get('name'))
#     return render(request, 'annotate.html', {'patient': patient})

def annotate_image(request, name):
    patient = get_object_or_404(Patient, name=name)
    return render(request, 'annotate.html', {'patient': patient})

# def annotate_image(request):
#     if 'name' in request.GET:
#         patient = get_object_or_404(Patient, name=request.GET.get('name'))
#     else:
#         # Handle the case where the name parameter is not provided
#         # For example, you could redirect to a page that asks the user to enter the patient's name
#         return redirect('patient_list')
#     return render(request, 'annotate.html', {'patient': patient})

# def annotate_image(request, patient_id):
#     patient = get_object_or_404(Patient, pk=patient_id)
#     return render(request, 'annotate.html', {'patient': patient})