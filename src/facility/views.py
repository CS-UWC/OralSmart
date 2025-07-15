from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Clinic
from django.core.mail import EmailMessage
from django.http import HttpResponse
from reports.views import generate_pdf
from patient.models import Patient
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from reportlab.lib.units import inch
from assessments.models import DentalScreening, DietaryScreening
from django.contrib import messages
from django.conf import settings



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
    """Generate PDF buffer for email attachment with enhanced styling"""
    buf = io.BytesIO()
    
    # Custom canvas class to add page decorations
    from reportlab.pdfgen.canvas import Canvas
    
    class CustomCanvas(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.page_template = None
            
        def showPage(self):
            if not self.page_template:
                self.page_template = CustomPageTemplate(self, None)
            self.page_template.draw_page_frame()
            super().showPage()
    
    # Create document template with custom canvas
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=90, leftMargin=90, 
                          topMargin=140, bottomMargin=80, canvasmaker=CustomCanvas)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Define blue color scheme
    blue_color = HexColor('#2E86AB')
    light_blue = HexColor('#A8DADC')
    
    # Custom styles with blue accents
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        spaceBefore=10,
        alignment=1,  # Center alignment
        textColor=blue_color,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=12,
        textColor=blue_color,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=light_blue,
        borderPadding=6,
        backColor=HexColor('#F8F9FA')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leftIndent=12,
        allowWidows=1,
        allowOrphans=1
    )
    
    # Build story (content)
    story = []
    
    # Title with date
    current_date = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph("OralSmart Dental Screening Report", title_style))
    story.append(Paragraph(f"Report Generated: {current_date}", ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        textColor=blue_color,
        spaceAfter=20
    )))
    
    # Patient Info with styled box
    story.append(Paragraph("Patient Information", heading_style))
    
    # Create patient info table for better layout
    patient_data = [
        [Paragraph(f"<b>Patient Name:</b> {patient.name}", normal_style), 
         Paragraph(f"<b>Patient Surname:</b> {patient.surname}", normal_style)],
        [Paragraph(f"<b>Patient Parent ID:</b> {patient.parent_id}", normal_style), 
         Paragraph(f"<b>Parent Contact:</b> {patient.parent_contact}", normal_style)]
    ]
    
    patient_table = Table(patient_data, colWidths=[3*inch, 3*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F0F8FF')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, light_blue),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 12))
    
    # Add screening availability info with styled display
    available_screenings = []
    if dental_data:
        available_screenings.append("✓ Dental Screening")
    if dietary_data:
        available_screenings.append("✓ Dietary Screening")
    
    story.append(Paragraph("Available Screening Data", heading_style))
    
    # Create screening status table
    screening_data = [[Paragraph(f"<b>Completed Screenings:</b> {', '.join(available_screenings)}", normal_style)]]
    screening_table = Table(screening_data, colWidths=[6*inch])
    screening_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#E8F4FD')),
        ('TEXTCOLOR', (0, 0), (-1, -1), blue_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, blue_color),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(screening_table)
    story.append(Spacer(1, 12))
    
    # Include dental screening sections if dental data exists
    if dental_data:
        # Section 1: Social/Behavioural/Medical Risk Factors (Dental)
        if 'section1' in selected_sections:
            story.append(Paragraph("Social/Behavioural/Medical Risk Factors (Dental Screening)", heading_style))
            
            section1_data = [
                f"<b>Caregiver treatment:</b> {dental_data.caregiver_treatment}",
                f"<b>South African Citizen:</b> {dental_data.sa_citizen}",
                f"<b>Special needs:</b> {dental_data.special_needs}"
            ]
            
            # Add each item as a paragraph for proper bold rendering
            for item in section1_data:
                story.append(Paragraph(item, normal_style))
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
            
            # Add each item as a paragraph for proper bold rendering
            for item in section2_data:
                story.append(Paragraph(item, normal_style))
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
            
            # Add each item as a paragraph for proper bold rendering
            for item in section3_data:
                story.append(Paragraph(item, normal_style))
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
            
            # Add each item as a paragraph for proper bold rendering
            for item in section4_data:
                story.append(Paragraph(item, normal_style))
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
            story.append(Paragraph(f"<b>Consumes:</b> {consumes}", normal_style))
            if daily:
                story.append(Paragraph(f"<b>Daily frequency:</b> {daily}", normal_style))
            if weekly:
                story.append(Paragraph(f"<b>Weekly frequency:</b> {weekly}", normal_style))
            story.append(Spacer(1, 8))

    # Build PDF
    doc.build(story)
    buf.seek(0)
    return buf

class CustomPageTemplate:
    """Custom page template with blue borders and logo"""
    
    def __init__(self, canvas_obj, doc):
        self.canvas = canvas_obj
        self.doc = doc
        
    def draw_page_frame(self):
        """Draw blue border and add logo/header to each page"""
        # Define blue color
        blue_color = HexColor('#2E86AB')  # Professional blue
        light_blue = HexColor('#A8DADC')  # Light blue for accents
        
        # Get page dimensions
        width, height = letter
        
        # Draw outer border (blue frame)
        self.canvas.setStrokeColor(blue_color)
        self.canvas.setLineWidth(3)
        self.canvas.rect(36, 36, width - 72, height - 72)  # 1 inch margin
        
        # Draw inner decorative border
        self.canvas.setStrokeColor(light_blue)
        self.canvas.setLineWidth(1)
        self.canvas.rect(45, 45, width - 90, height - 90)
        
        # Add header background
        self.canvas.setFillColor(light_blue)
        self.canvas.rect(45, height - 120, width - 90, 30, fill=1, stroke=0)
        
        # Add logo (if exists)
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'Logo2.png')
        if os.path.exists(logo_path):
            try:
                # Draw logo in top-left corner with better size and positioning
                self.canvas.drawImage(logo_path, 60, height - 115, width=100, height=30, 
                                    preserveAspectRatio=True, mask='auto')
            except Exception as e:
                # Add text fallback if logo can't be loaded
                self.canvas.setFillColor(blue_color)
                self.canvas.setFont('Helvetica-Bold', 12)
                self.canvas.drawString(60, height - 105, "OralSmart")
        
        # Add "OralSmart" text in header
        self.canvas.setFillColor(blue_color)
        self.canvas.setFont('Helvetica-Bold', 16)
        self.canvas.drawString(180, height - 105, "OralSmart Dental Care System")
        
        # Add current date in top-right corner
        current_date = datetime.now().strftime("%B %d, %Y")
        self.canvas.setFillColor(blue_color)
        self.canvas.setFont('Helvetica', 10)
        date_width = self.canvas.stringWidth(f"Generated: {current_date}")
        self.canvas.drawString(width - 90 - date_width, height - 105, f"Generated: {current_date}")
        
        # Add footer with page number
        self.canvas.setFillColor(blue_color)
        self.canvas.setFont('Helvetica', 9)
        footer_text = f"Page {self.canvas.getPageNumber()}"
        footer_width = self.canvas.stringWidth(footer_text)
        self.canvas.drawString((width - footer_width) / 2, 50, footer_text)
        
        # Reset colors for content
        self.canvas.setFillColor(colors.black)
        self.canvas.setStrokeColor(colors.black)

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

