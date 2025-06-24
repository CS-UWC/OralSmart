from django.shortcuts import render

from patient.models import Patient

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from assessments.models import DentalScreening
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt

# Create your views here.

# def view_report(request, patient_id):

#     data = DentalScreening.objects.get(pk=patient_id)

#     buf = io.BytesIO()

#     c = canvas.Canvas(buf, pagesize=letter, bottomup=0)

#     textobj = c.beginText()
#     textobj.setTextOrigin(inch, inch)
#     textobj.setFont('Helvetica', 14)

#     # Example: Add some data from the DentalScreening instance to the PDF
#     textobj.textLine(f"Patient ID: {data.pk}")
#     # Add more fields as needed, e.g. textobj.textLine(f"Field: {data.some_field}")

#     c.drawText(textobj)
#     c.showPage()
#     c.save()
#     buf.seek(0)

#     return FileResponse(buf, as_attachment=True, filename='report.pdf')

def view_report(request, patient_id):
    return render(request, "reports/report.html", {"patient_id": patient_id})

#@login_required
@xframe_options_exempt
def generate_pdf(request, patient_id):

    patient =Patient.objects.get(pk=patient_id)

    allowed_sections = {'section1', 'section2', 'section3', 'section4', 'section5'}

    if request.method == "POST":
        selected_sections = request.POST.get('selected_sections', '').split(',')
        selected_sections = [s for s in selected_sections if s in allowed_sections]   
        request.session['selected_sections'] = selected_sections  # Save for GET
        return HttpResponse(status=204)#return render(request, "reports/report.html", {"patient_id": patient_id})
    else:
        # For GET, generate PDF with last selected sections
        selected_sections = request.session.get('selected_sections', [
            'section1', 'section2', 'section3', 'section4', 'section5'
        ])

        selected_sections = [s for s in selected_sections if s in allowed_sections]

        try:
            data = DentalScreening.objects.get(patient_id=patient_id)
        except DentalScreening.DoesNotExist:
            return render(request, "reports/report.html", {
                "patient_id": patient_id,
                "messages": ["No dental screening found for this patient."]
            })
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
        textobj = c.beginText()
        textobj.setTextOrigin(inch, inch)
        textobj.setFont('Helvetica', 14)

        textobj.textLine(" ")
        textobj.textLine("Patient Name: " + patient.name)
        textobj.textLine("Patient Surname: " + patient.surname)
        textobj.textLine("Patient Parent ID " + patient.parent_id)
        textobj.textLine("Patient Parent Contact Number: " + patient.parent_contact)
        textobj.textLine("")

        # Add only the selected sections
        if 'section1' in selected_sections:
            textobj.textLine(" ")
            textobj.textLine("Social/Behavioural/Medical Risk Factors")
            textobj.textLine(f"Caregiver treatment: {data.caregiver_treatment}")
            textobj.textLine(f"Income: {data.income}")
            textobj.textLine(f"Sugary meals: {data.sugar_meals}")
            textobj.textLine(f"Sugar snacks: {data.sugar_snacks}")
            textobj.textLine(f"Sugar beverages: {data.sugar_beverages}")
            textobj.textLine(f"South African Citizen: {data.sa_citizen}")
            textobj.textLine(f"Special_needs: {data.special_needs}")

        if 'section2' in selected_sections:
            textobj.textLine(" ")
            textobj.textLine("Clinical Risk Factors")
            textobj.textLine(f"Plaque: {data.plaque}")
            textobj.textLine(f"Dry mouth: {data.dry_mouth}")
            textobj.textLine(f"Enamel defects: {data.enamel_defects}")
            textobj.textLine(f"Intra-oral appliance: {data.appliance}")

        if 'section3' in selected_sections:
            textobj.textLine(" ")
            textobj.textLine("Protective Factors")
            textobj.textLine(f"Fluoride water: {data.fluoride_water}")
            textobj.textLine(f"Fluoride toothpaste: {data.fluoride_toothpaste}")
            textobj.textLine(f"Topical fluoride: {data.topical_fluoride}")
            textobj.textLine(f"Regular checkups: {data.regular_checkups}")

        if 'section4' in selected_sections:
            textobj.textLine(" ")
            textobj.textLine("Disease Indicators")
            textobj.textLine(f"Sealed pits: {data.sealed_pits}")
            textobj.textLine(f"Restorative procedures: {data.restorative_procedures}")
            textobj.textLine(f"Enamel change: {data.enamel_change}")
            textobj.textLine(f"Dentin discoloration: {data.dentin_discoloration}")
            textobj.textLine(f"White spot lesions: {data.white_spot_lesions}")
            textobj.textLine(f"Cavitated lesions: {data.cavitated_lesions}")
            textobj.textLine(f"Multiple restorations: {data.multiple_restorations}")
            textobj.textLine(f"Missing teeth: {data.missing_teeth}")

        if 'section5' in selected_sections:

            tooth_names = {
                # Permanent Teeth
                "tooth_18": "Upper Right Third Molar (Wisdom Tooth)",
                "tooth_17": "Upper Right Second Molar",
                "tooth_16": "Upper Right First Molar",
                "tooth_15": "Upper Right Second Premolar",
                "tooth_14": "Upper Right First Premolar",
                "tooth_13": "Upper Right Canine",
                "tooth_12": "Upper Right Lateral Incisor",
                "tooth_11": "Upper Right Central Incisor",
                "tooth_21": "Upper Left Central Incisor",
                "tooth_22": "Upper Left Lateral Incisor",
                "tooth_23": "Upper Left Canine",
                "tooth_24": "Upper Left First Premolar",
                "tooth_25": "Upper Left Second Premolar",
                "tooth_26": "Upper Left First Molar",
                "tooth_27": "Upper Left Second Molar",
                "tooth_28": "Upper Left Third Molar (Wisdom Tooth)",
                "tooth_48": "Lower Right Third Molar (Wisdom Tooth)",
                "tooth_47": "Lower Right Second Molar",
                "tooth_46": "Lower Right First Molar",
                "tooth_45": "Lower Right Second Premolar",
                "tooth_44": "Lower Right First Premolar",
                "tooth_43": "Lower Right Canine",
                "tooth_42": "Lower Right Lateral Incisor",
                "tooth_41": "Lower Right Central Incisor",
                "tooth_31": "Lower Left Central Incisor",
                "tooth_32": "Lower Left Lateral Incisor",
                "tooth_33": "Lower Left Canine",
                "tooth_34": "Lower Left First Premolar",
                "tooth_35": "Lower Left Second Premolar",
                "tooth_36": "Lower Left First Molar",
                "tooth_37": "Lower Left Second Molar",
                "tooth_38": "Lower Left Third Molar (Wisdom Tooth)",

                # Primary (Deciduous) Teeth
                "tooth_55": "Upper Right Second Primary Molar",
                "tooth_54": "Upper Right First Primary Molar",
                "tooth_53": "Upper Right Primary Canine",
                "tooth_52": "Upper Right Lateral Primary Incisor",
                "tooth_51": "Upper Right Central Primary Incisor",
                "tooth_61": "Upper Left Central Primary Incisor",
                "tooth_62": "Upper Left Lateral Primary Incisor",
                "tooth_63": "Upper Left Primary Canine",
                "tooth_64": "Upper Left First Primary Molar",
                "tooth_65": "Upper Left Second Primary Molar",
                "tooth_85": "Lower Right Second Primary Molar",
                "tooth_84": "Lower Right First Primary Molar",
                "tooth_83": "Lower Right Primary Canine",
                "tooth_82": "Lower Right Lateral Primary Incisor",
                "tooth_81": "Lower Right Central Primary Incisor",
                "tooth_71": "Lower Left Central Primary Incisor",
                "tooth_72": "Lower Left Lateral Primary Incisor",
                "tooth_73": "Lower Left Primary Canine",
                "tooth_74": "Lower Left First Primary Molar",
                "tooth_75": "Lower Left Second Primary Molar"
            }

            textobj.textLine(" ")
            textobj.textLine("DMFT Assessment")

            for code, status in data.teeth_data.items():
                if status:  # Only show teeth with some status
                    textobj.textLine(f"{tooth_names.get(code, 'Unknown Tooth')} ({code}): Status = {status}")
                elif status == "":
                    textobj.textLine(f"{tooth_names.get(code, 'Unknown Tooth')} ({code}): Status = No Issue (Assumed)")
                    

        c.drawText(textobj)
        c.showPage()
        c.save()
        buf.seek(0)

        #return FileResponse(buf, as_attachment=False, filename='report.pdf', content_type='application/pdf')        #patient_name = data.patient.first_name + "_" + data.patient.last_name if data.patient else "unknown"
        filename = f"report_{patient.name}_{patient.surname}_{patient_id}.pdf"
        return FileResponse(buf, as_attachment=False, filename=filename, content_type='application/pdf')
    