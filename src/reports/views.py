from django.shortcuts import render
from patient.models import Patient
from django.http import FileResponse
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
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
        #For GET, generate PDF with last selected sections
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
        
        #Create document template
        doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        
        #Get styles
        styles = getSampleStyleSheet()
        
        #Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  #Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12,
        )
        
        normal_style = styles['Normal']
        
        #Build story (content)
        story = []
        
        #Title
        story.append(Paragraph("OralSmart Dental Screening Report", title_style))
        story.append(Spacer(1, 12))
        
        #Patient Info
        story.append(Paragraph("Patient Information", heading_style))
        story.append(Paragraph(f"<b>Patient Name:</b> {patient.name}", normal_style))
        story.append(Paragraph(f"<b>Patient Surname:</b> {patient.surname}", normal_style))
        story.append(Paragraph(f"<b>Patient Parent ID:</b> {patient.parent_id}", normal_style))
        story.append(Paragraph(f"<b>Patient Parent Contact:</b> {patient.parent_contact}", normal_style))
        story.append(Spacer(1, 12))
        
        #Section 1: Social/Behavioural/Medical Risk Factors
        if 'section1' in selected_sections:
            story.append(Paragraph("Social/Behavioural/Medical Risk Factors", heading_style))
            
            section1_data = [
                f"<b>Caregiver treatment:</b> {data.caregiver_treatment}",
                f"<b>Income:</b> {data.income}",
                f"<b>Sugary meals:</b> {data.sugar_meals}",
                f"<b>Sugar snacks:</b> {data.sugar_snacks}",
                f"<b>Sugar beverages:</b> {data.sugar_beverages}",
                f"<b>South African Citizen:</b> {data.sa_citizen}",
                f"<b>Special needs:</b> {data.special_needs}"
            ]
            
            for line in section1_data:
                story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

        #Section 2: Clinical Risk Factors
        if 'section2' in selected_sections:
            story.append(Paragraph("Clinical Risk Factors", heading_style))
            
            section2_data = [
                f"<b>Plaque:</b> {data.plaque}",
                f"<b>Dry mouth:</b> {data.dry_mouth}",
                f"<b>Enamel defects:</b> {data.enamel_defects}",
                f"<b>Intra-oral appliance:</b> {data.appliance}"
            ]
            
            for line in section2_data:
                story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

        #Section 3: Protective Factors
        if 'section3' in selected_sections:
            story.append(Paragraph("Protective Factors", heading_style))
            
            section3_data = [
                f"<b>Fluoride water:</b> {data.fluoride_water}",
                f"<b>Fluoride toothpaste:</b> {data.fluoride_toothpaste}",
                f"<b>Topical fluoride:</b> {data.topical_fluoride}",
                f"<b>Regular checkups:</b> {data.regular_checkups}"
            ]
            
            for line in section3_data:
                story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

        #Section 4: Disease Indicators
        if 'section4' in selected_sections:
            story.append(Paragraph("Disease Indicators", heading_style))
            
            section4_data = [
                f"<b>Sealed pits:</b> {data.sealed_pits}",
                f"<b>Restorative procedures:</b> {data.restorative_procedures}",
                f"<b>Enamel change:</b> {data.enamel_change}",
                f"<b>Dentin discoloration:</b> {data.dentin_discoloration}",
                f"<b>White spot lesions:</b> {data.white_spot_lesions}",
                f"<b>Cavitated lesions:</b> {data.cavitated_lesions}",
                f"<b>Multiple restorations:</b> {data.multiple_restorations}",
                f"<b>Missing teeth:</b> {data.missing_teeth}"
            ]
            
            for line in section4_data:
                story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

        #Section 5: DMFT Assessment starts here
        if 'section5' in selected_sections:
            tooth_names = {
                #Permanent Teeth
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
                #Primary Teeth
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

            story.append(Paragraph("DMFT Assessment", heading_style))
            
            #add a new page for tooth data
            story.append(PageBreak())
            story.append(Paragraph("Tooth Assessment", heading_style))

            for code, status in data.teeth_data.items():
                if status:
                    text = f"<b>{tooth_names.get(code, 'Unknown Tooth')} ({code}):</b> {status}"
                    story.append(Paragraph(text, normal_style))
                elif status == "":
                    text = f"<b>{tooth_names.get(code, 'Unknown Tooth')} ({code}):</b> No Issue (Assumed)"
                    story.append(Paragraph(text, normal_style))

        #build PDF
        doc.build(story)
        buf.seek(0)

        filename = f"report_{patient.name}_{patient.surname}_{patient_id}.pdf"
        return FileResponse(buf, as_attachment=False, filename=filename, content_type='application/pdf')