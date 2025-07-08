from django.shortcuts import render
from patient.models import Patient
from django.http import FileResponse, HttpResponse
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from assessments.models import DentalScreening, DietaryScreening
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.mail import EmailMessage
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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
    return render(
        request, 
        "reports/report.html", 
        {
            "patient_id": patient_id,
            'show_navbar': True,
        }
    )

#@login_required
@xframe_options_exempt
def generate_pdf(request, patient_id):

    try:
        patient = Patient.objects.get(pk=patient_id)
    except Patient.DoesNotExist:
        # Return a PDF with error message for missing patient
        # This ensures the iframe always gets PDF content, not HTML
        from reportlab.pdfgen import canvas
        
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Error: Patient Not Found")
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, f"No patient found with ID: {patient_id}")
        c.drawString(100, 700, "Please check the patient ID and try again.")
        
        c.showPage()
        c.save()
        buf.seek(0)
        
        return FileResponse(buf, as_attachment=False, filename="error.pdf", content_type='application/pdf')

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
            dental_data = DentalScreening.objects.get(patient_id=patient_id)
        except DentalScreening.DoesNotExist:
            dental_data = None
            
        try:
            dietary_data = DietaryScreening.objects.get(patient_id=patient_id)
        except DietaryScreening.DoesNotExist:
            dietary_data = None
            
        # Check if we have at least one type of screening data
        if not dental_data and not dietary_data:
            # Return a PDF with error message instead of HTML
            # This prevents the iframe from displaying a nested HTML page
            from reportlab.pdfgen import canvas
            
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=letter)
            
            # Add error message to PDF
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 750, "Error: No Screening Data Found")
            c.setFont("Helvetica", 12)
            c.drawString(100, 720, f"No screening data found for patient ID: {patient_id}")
            c.drawString(100, 700, "Please complete at least one screening before generating a report.")
            c.drawString(100, 680, "Available screenings: Dental Screening, Dietary Screening")
            
            c.showPage()
            c.save()
            buf.seek(0)
            
            return FileResponse(buf, as_attachment=False, filename="error.pdf", content_type='application/pdf')
        
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
        
        # Add screening availability info
        available_screenings = []
        if dental_data:
            available_screenings.append("Dental Screening")
        if dietary_data:
            available_screenings.append("Dietary Screening")
        
        story.append(Paragraph("Available Screening Data", heading_style))
        story.append(Paragraph(f"<b>Completed Screenings:</b> {', '.join(available_screenings)}", normal_style))
        story.append(Spacer(1, 12))
        
        # Include dental screening sections if dental data exists
        if dental_data:
            #Section 1: Social/Behavioural/Medical Risk Factors (Dental)
            if 'section1' in selected_sections:
                story.append(Paragraph("Social/Behavioural/Medical Risk Factors (Dental Screening)", heading_style))
                
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

            #Section 2: Clinical Risk Factors (Dental)
            if 'section2' in selected_sections:
                story.append(Paragraph("Clinical Risk Factors (Dental Screening)", heading_style))
                
                section2_data = [
                    f"<b>Plaque:</b> {dental_data.plaque}",
                    f"<b>Dry mouth:</b> {dental_data.dry_mouth}",
                    f"<b>Enamel defects:</b> {dental_data.enamel_defects}",
                    f"<b>Intra-oral appliance:</b> {dental_data.appliance}"
                ]
                
                for line in section2_data:
                    story.append(Paragraph(line, normal_style))
                story.append(Spacer(1, 12))

            #Section 3: Protective Factors (Dental)
            if 'section3' in selected_sections:
                story.append(Paragraph("Protective Factors (Dental Screening)", heading_style))
                
                section3_data = [
                    f"<b>Fluoride water:</b> {dental_data.fluoride_water}",
                    f"<b>Fluoride toothpaste:</b> {dental_data.fluoride_toothpaste}",
                    f"<b>Topical fluoride:</b> {dental_data.topical_fluoride}",
                    f"<b>Regular checkups:</b> {dental_data.regular_checkups}"
                ]
            
                for line in section3_data:
                    story.append(Paragraph(line, normal_style))
                story.append(Spacer(1, 12))

            #Section 4: Disease Indicators (Dental)
            if 'section4' in selected_sections:
                story.append(Paragraph("Disease Indicators (Dental Screening)", heading_style))
                
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

            #Section 5: DMFT Assessment (Dental only)
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

                story.append(Paragraph("DMFT Assessment (Dental Screening)", heading_style))
                
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
                        
        # Include dietary screening sections if dietary data exists
        if dietary_data:
            story.append(Paragraph("Dietary Screening Results", heading_style))
            
            dietary_sections = [
                ("Sweet/Sugary Foods", dietary_data.sweet_sugary_foods, dietary_data.sweet_sugary_foods_daily, dietary_data.sweet_sugary_foods_weekly),
                ("Cold Drinks and Juices", dietary_data.cold_drinks_juices, dietary_data.cold_drinks_juices_daily, dietary_data.cold_drinks_juices_weekly),
                ("Take-aways and Processed Foods", dietary_data.takeaways_processed_foods, dietary_data.takeaways_processed_foods_daily, dietary_data.takeaways_processed_foods_weekly),
                ("Salty Snacks", dietary_data.salty_snacks, dietary_data.salty_snacks_daily, dietary_data.salty_snacks_weekly),
                ("Spreads", dietary_data.spreads, dietary_data.spreads_daily, dietary_data.spreads_weekly)
            ]
            
            for section_name, consumes, daily, weekly in dietary_sections:
                story.append(Paragraph(f"<b>{section_name}</b>", normal_style))
                story.append(Paragraph(f"Consumes: {consumes}", normal_style))
                if daily:
                    story.append(Paragraph(f"Daily frequency: {daily}", normal_style))
                if weekly:
                    story.append(Paragraph(f"Weekly frequency: {weekly}", normal_style))
                story.append(Spacer(1, 8))

        #build PDF
        doc.build(story)
        buf.seek(0)

        filename = f"report_{patient.name}_{patient.surname}_{patient_id}.pdf"
        return FileResponse(buf, as_attachment=False, filename=filename, content_type='application/pdf')

def send_report_email(request, patient_id):
    """Send report via email to user and CC health professionals"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)
    
    try:
        patient = Patient.objects.get(pk=patient_id)
    except Patient.DoesNotExist:
        return HttpResponse('Patient not found', status=404)
    
    # Get form data
    recipient_email = request.POST.get('recipient_email')
    cc_emails = request.POST.get('cc_emails', '').strip()
    subject = request.POST.get('subject', f'OralSmart Dental Report - {patient.name} {patient.surname}')
    message_text = request.POST.get('message', '')
    
    if not recipient_email:
        return HttpResponse('Recipient email is required', status=400)
    
    # Parse CC emails (comma-separated)
    cc_list = []
    if cc_emails:
        cc_list = [email.strip() for email in cc_emails.split(',') if email.strip()]
    
    try:
        # Get selected sections from session
        selected_sections = request.session.get('selected_sections', [
            'section1', 'section2', 'section3', 'section4', 'section5'
        ])
        
        # Generate PDF report
        pdf_buffer = generate_pdf_buffer(patient, selected_sections)
        
        # Create email context
        email_context = {
            'patient_name': f'{patient.name} {patient.surname}',
            'patient_id': patient_id,
            'message': message_text,
            'sections_included': ', '.join([
                section.replace('section', 'Section ') for section in selected_sections
            ]),
            'sender_name': request.user.get_full_name() if request.user.is_authenticated else 'OralSmart Team'
        }
        
        # Render email template
        html_message = render_to_string('reports/email_template.html', email_context)
        plain_message = strip_tags(html_message)
        
        # Create email
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
            cc=cc_list,
        )
        
        # Attach PDF
        filename = f"dental_report_{patient.name}_{patient.surname}_{patient_id}.pdf"
        email.attach(filename, pdf_buffer.getvalue(), 'application/pdf')
        
        # Send email
        email.send()
        
        logger.info(f"Report email sent for patient {patient_id} to {recipient_email}")
        if cc_list:
            logger.info(f"CC recipients: {', '.join(cc_list)}")
        
        return HttpResponse('Email sent successfully', status=200)
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return HttpResponse(f'Error sending email: {str(e)}', status=500)

def generate_pdf_buffer(patient, selected_sections):
    """Generate PDF buffer for email attachment"""
    try:
        dental_data = DentalScreening.objects.get(patient_id=patient.id)
    except DentalScreening.DoesNotExist:
        dental_data = None
        
    try:
        dietary_data = DietaryScreening.objects.get(patient_id=patient.id)
    except DietaryScreening.DoesNotExist:
        dietary_data = None
    
    buf = io.BytesIO()
    
    # Create document template
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=12,
    )
    
    normal_style = styles['Normal']
    
    # Build story (content)
    story = []
    
    # Title
    story.append(Paragraph("OralSmart Dental Screening Report", title_style))
    story.append(Spacer(1, 12))
    
    # Patient Info
    story.append(Paragraph("Patient Information", heading_style))
    story.append(Paragraph(f"<b>Patient Name:</b> {patient.name}", normal_style))
    story.append(Paragraph(f"<b>Patient Surname:</b> {patient.surname}", normal_style))
    story.append(Paragraph(f"<b>Patient Parent ID:</b> {patient.parent_id}", normal_style))
    story.append(Paragraph(f"<b>Patient Parent Contact:</b> {patient.parent_contact}", normal_style))
    story.append(Spacer(1, 12))
    
    # Add screening availability info
    available_screenings = []
    if dental_data:
        available_screenings.append("Dental Screening")
    if dietary_data:
        available_screenings.append("Dietary Screening")
    
    story.append(Paragraph("Available Screening Data", heading_style))
    story.append(Paragraph(f"<b>Completed Screenings:</b> {', '.join(available_screenings)}", normal_style))
    story.append(Spacer(1, 12))
    
    # Include dental screening sections if dental data exists
    if dental_data:
        # Section 1: Social/Behavioural/Medical Risk Factors (Dental)
        if 'section1' in selected_sections:
            story.append(Paragraph("Social/Behavioural/Medical Risk Factors (Dental Screening)", heading_style))
            
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

        # Section 2: Clinical Risk Factors (Dental)
        if 'section2' in selected_sections:
            story.append(Paragraph("Clinical Risk Factors (Dental Screening)", heading_style))
            
            section2_data = [
                f"<b>Plaque:</b> {dental_data.plaque}",
                f"<b>Dry mouth:</b> {dental_data.dry_mouth}",
                f"<b>Enamel defects:</b> {dental_data.enamel_defects}",
                f"<b>Intra-oral appliance:</b> {dental_data.appliance}"
            ]
            
            for line in section2_data:
                story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

        # Section 3: Protective Factors (Dental)
        if 'section3' in selected_sections:
            story.append(Paragraph("Protective Factors (Dental Screening)", heading_style))
            
            section3_data = [
                f"<b>Fluoride water:</b> {dental_data.fluoride_water}",
                f"<b>Fluoride toothpaste:</b> {dental_data.fluoride_toothpaste}",
                f"<b>Topical fluoride:</b> {dental_data.topical_fluoride}",
                f"<b>Regular checkups:</b> {dental_data.regular_checkups}"
            ]
        
            for line in section3_data:
                story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

        # Section 4: Disease Indicators (Dental)
        if 'section4' in selected_sections:
            story.append(Paragraph("Disease Indicators (Dental Screening)", heading_style))
            
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

        # Section 5: DMFT Assessment (Dental only)
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
                # Primary Teeth
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

            story.append(Paragraph("DMFT Assessment (Dental Screening)", heading_style))
            
            # Add a new page for tooth data
            story.append(PageBreak())
            story.append(Paragraph("Tooth Assessment", heading_style))

            for code, status in dental_data.teeth_data.items():
                if status:
                    text = f"<b>{tooth_names.get(code, 'Unknown Tooth')} ({code}):</b> {status}"
                    story.append(Paragraph(text, normal_style))
                elif status == "":
                    text = f"<b>{tooth_names.get(code, 'Unknown Tooth')} ({code}):</b> No Issue (Assumed)"
                    story.append(Paragraph(text, normal_style))
                    
    # Include dietary screening sections if dietary data exists
    if dietary_data:
        story.append(Paragraph("Dietary Screening Results", heading_style))
        
        dietary_sections = [
            ("Sweet/Sugary Foods", dietary_data.sweet_sugary_foods, dietary_data.sweet_sugary_foods_daily, dietary_data.sweet_sugary_foods_weekly),
            ("Cold Drinks and Juices", dietary_data.cold_drinks_juices, dietary_data.cold_drinks_juices_daily, dietary_data.cold_drinks_juices_weekly),
            ("Take-aways and Processed Foods", dietary_data.takeaways_processed_foods, dietary_data.takeaways_processed_foods_daily, dietary_data.takeaways_processed_foods_weekly),
            ("Salty Snacks", dietary_data.salty_snacks, dietary_data.salty_snacks_daily, dietary_data.salty_snacks_weekly),
            ("Spreads", dietary_data.spreads, dietary_data.spreads_daily, dietary_data.spreads_weekly)
        ]
        
        for section_name, consumes, daily, weekly in dietary_sections:
            story.append(Paragraph(f"<b>{section_name}</b>", normal_style))
            story.append(Paragraph(f"Consumes: {consumes}", normal_style))
            if daily:
                story.append(Paragraph(f"Daily frequency: {daily}", normal_style))
            if weekly:
                story.append(Paragraph(f"Weekly frequency: {weekly}", normal_style))
            story.append(Spacer(1, 8))

    # Build PDF
    doc.build(story)
    buf.seek(0)
    
    return buf