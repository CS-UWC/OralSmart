from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Clinic
from django.core.mail import EmailMessage
from django.http import HttpResponse
from reports.views import generate_pdf
from patient.models import Patient
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from assessments.models import DentalScreening, DietaryScreening
from django.contrib import messages



def clinic_list(request):
    """View to retrieve and display all clinic objects with search functionality"""
    search_query = request.GET.get('search', '')
    center_type = request.GET.get('center_type', '')
    
    #start with all clinics
    clinics = Clinic.objects.all()
    
    #apply center type filter if selected
    if center_type:
        clinics = clinics.filter(clinic_type=center_type)
    
    #apply search filter if provided
    if search_query:
        clinics = clinics.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    patient_id = request.GET.get('patient_id')
    selected_sections = request.GET.get('selected_sections', '').split(',') if request.GET.get('selected_sections') else []
    context = {
        'clinics': clinics,
        'search_query': search_query,
        'center_type': center_type,
        'patient_id': patient_id,
        'selected_sections': selected_sections,
    }
    return render(request, 'facility/clinic_list.html', context)

def generate_pdf_buffer(patient, dental_data, dietary_data, selected_sections):
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
    if 'section1' in selected_sections and dental_data:
        story.append(Paragraph("Social/Behavioural/Medical Risk Factors", heading_style))
        
        section1_data = [
            f"<b>Caregiver treatment:</b> {dental_data.caregiver_treatment}",
            f"<b>Income:</b> {dental_data.income}",
            f"<b>Sugary meals:</b> {dental_data.sugar_meals}",
            f"<b>Sugar snacks:</b> {dental_data.sugar_snacks}",
            f"<b>Sugar beverages:</b> {dental_data.sugar_beverages}",
            f"<b>South African Citizen:</b> {dental_data.sa_citizen}",
            f"<b>Special needs:</b> {dental_data.special_needs}"
        ]
        
        for line in section1_data:
            story.append(Paragraph(line, normal_style))
        story.append(Spacer(1, 12))

    #Section 2: Clinical Risk Factors
    if 'section2' in selected_sections and dental_data:
        story.append(Paragraph("Clinical Risk Factors", heading_style))
        
        section2_data = [
            f"<b>Plaque:</b> {dental_data.plaque}",
            f"<b>Dry mouth:</b> {dental_data.dry_mouth}",
            f"<b>Enamel defects:</b> {dental_data.enamel_defects}",
            f"<b>Intra-oral appliance:</b> {dental_data.appliance}"
        ]
        
        for line in section2_data:
            story.append(Paragraph(line, normal_style))
        story.append(Spacer(1, 12))

    #Section 3: Protective Factors
    if 'section3' in selected_sections and dental_data:
        story.append(Paragraph("Protective Factors", heading_style))
        
        section3_data = [
            f"<b>Fluoride water:</b> {dental_data.fluoride_water}",
            f"<b>Fluoride toothpaste:</b> {dental_data.fluoride_toothpaste}",
            f"<b>Topical fluoride:</b> {dental_data.topical_fluoride}",
            f"<b>Regular checkups:</b> {dental_data.regular_checkups}"
        ]
        
        for line in section3_data:
            story.append(Paragraph(line, normal_style))
        story.append(Spacer(1, 12))

    #Section 4: Disease Indicators
    if 'section4' in selected_sections and dental_data:
        story.append(Paragraph("Disease Indicators", heading_style))
        
        section4_data = [
            f"<b>Sealed pits:</b> {dental_data.sealed_pits}",
            f"<b>Restorative procedures:</b> {dental_data.restorative_procedures}",
            f"<b>Enamel change:</b> {dental_data.enamel_change}",
            f"<b>Dentin discoloration:</b> {dental_data.dentin_discoloration}",
            f"<b>White spot lesions:</b> {dental_data.white_spot_lesions}",
            f"<b>Cavitated lesions:</b> {dental_data.cavitated_lesions}",
            f"<b>Multiple restorations:</b> {dental_data.multiple_restorations}",
            f"<b>Missing teeth:</b> {dental_data.missing_teeth}"
        ]
        
        for line in section4_data:
            story.append(Paragraph(line, normal_style))
        story.append(Spacer(1, 12))

    #Section 5: DMFT Assessment starts here
    if 'section5' in selected_sections and dental_data:
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

        for code, status in dental_data.teeth_data.items():
            if status:
                text = f"<b>{tooth_names.get(code, 'Unknown Tooth')} ({code}):</b> {status}"
                story.append(Paragraph(text, normal_style))
            elif status == "":
                text = f"<b>{tooth_names.get(code, 'Unknown Tooth')} ({code}):</b> No Issue (Assumed)"
                story.append(Paragraph(text, normal_style))

    # Add dietary screening sections if dietary_data exists
    if dietary_data:
        story.append(Paragraph("Dietary Screening Results", heading_style))
        # ...add dietary fields as needed...
    #build PDF

    doc.build(story)
    buf.seek(0)
    return buf

def refer_patient(request, clinic_id):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        if not patient_id:
            return HttpResponse("Missing patient_id", status=400)
        selected_sections = request.POST['selected_sections'].split(',')
        appointment_date = request.POST['appointment_date']
        appointment_time = request.POST['appointment_time']
        clinic = Clinic.objects.get(pk=clinic_id)
        patient = Patient.objects.get(pk=patient_id)
        try:
            dental_data = DentalScreening.objects.get(patient_id=patient_id)
        except DentalScreening.DoesNotExist:
            dental_data = None
        try:
            dietary_data = DietaryScreening.objects.get(patient_id=patient_id)
        except DietaryScreening.DoesNotExist:
            dietary_data = None
        if not dental_data and not dietary_data:
            messages.error(request, "No screening found for this patient. Please complete at least one screening before referral.")
            return redirect('clinics')
        pdf_buffer = generate_pdf_buffer(patient, dental_data, dietary_data, selected_sections)
        # Compose and send email
        recipient_list = [clinic.email] if clinic.email else []
        email = EmailMessage(
            subject=f"Referral for {patient.name} {patient.surname}",
            body=f"Patient {patient.name} {patient.surname} is referred for an appointment on {appointment_date} at {appointment_time}.",
            to=recipient_list,
        )
        email.attach(f"report_{patient.name}_{patient.surname}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        email.send()
        return render(request, 'facility/referral_success.html', {'clinic': clinic})
    else:
        return HttpResponse(status=405)

