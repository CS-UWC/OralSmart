from django.shortcuts import render

from patient.models import Patient

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter



# Create your views here.


def view_report(request):

    return render(request, "reports/report.html", {})

def generate_pdf(request, patient_id):

        return render(request, "reports/report.html", {})
