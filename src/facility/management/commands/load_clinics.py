from django.core.management.base import BaseCommand
from facility.models import Clinic


class Command(BaseCommand):
    help = 'Load clinic data from the SQL file into the database'

    def handle(self, *args, **options):
        """Load clinic data from the facility_clinic.sql file"""
        
        # Clinic data extracted from the SQL file
        clinics_data = [
            {
                'id': 1,
                'name': "Adriaanse Clinic",
                'address': "40th Avenue, Clarke's Estate, Elsies River, Cape Town, 7490",
                'phone_number': "021 444 2396",
                'email': "kungfuvee001@gmail.com",
                'website': None,
                'description': None,
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 2,
                'name': "Alphen Clinic",
                'address': "Main Rd, Constantia, Cape Town",
                'phone_number': "021 444 9628",
                'email': "alphen.clinic@capetown.gov.za",
                'website': "http://www.westerncape.gov.za/",
                'description': "Public health clinic",
                'hours': "Mon–Fri: 08:00–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 3,
                'name': "Elsies River Community Health Centre",
                'address': "Corner of 29th Avenue and Halt Road, Elsies River, Cape Town",
                'phone_number': "021 931 0211",
                'email': "lunga.makamba@westerncape.gov.za",
                'website': None,
                'description': "Community Health Centre",
                'hours': "Emergency 24 h; Primary HC Mon–Fri 07:00–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 4,
                'name': "Blue Downs Clinic",
                'address': "Bentley Road, Blue Downs, Cape Town, 7100",
                'phone_number': "021 444 8313",
                'email': "bluedowns.health@capetown.gov.za",
                'website': None,
                'description': None,
                'hours': None,
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 5,
                'name': "Brackenfell Clinic",
                'address': "Paradys Street, Brackenfell, Cape Town, 7560",
                'phone_number': "021 980 1285",
                'email': None,
                'website': "http://www.westerncape.gov.za/",
                'description': None,
                'hours': "Mon–Fri: 07:30–16:30",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 6,
                'name': "Northpine Clinic",
                'address': "Northpine Drive, Brackenfell, Cape Town, 7560",
                'phone_number': "021 983 6360",
                'email': "northpine.clinic@capetown.gov.za",
                'website': None,
                'description': "Operates in Oostenberg Health District",
                'hours': None,
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 7,
                'name': "Fish Hoek Clinic",
                'address': "61 Central Circle, Fish Hoek, Cape Town, 7975",
                'phone_number': "021 784 2660",
                'email': "fishhoek.clinic@capetown.gov.za",
                'website': None,
                'description': "Community health clinic",
                'hours': "Mon–Wed: 08:00–16:00; Thu: 14:00–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 8,
                'name': "Medicross Fish Hoek",
                'address': "23 5th Avenue, Fish Hoek, Cape Town, 7975",
                'phone_number': "021 782 3506",
                'email': "fishhoek@medicross.co.za",
                'website': "http://www.medicross.co.za",
                'description': "Private GP and travel clinic",
                'hours': "Mon–Fri: 08:30–18:00; Sat: 08:30–14:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 9,
                'name': "Gugulethu Clinic",
                'address': "C/o NY1 & NY3, Gugulethu, Cape Town",
                'phone_number': "021 444 6059",
                'email': "guguletu.clinic@capetown.gov.za",
                'website': None,
                'description': "Public health clinic, Nyanga district",
                'hours': None,
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 10,
                'name': "Guguletu Community Health Clinic",
                'address': "NY3, Gugulethu, Cape Town, 7760",
                'phone_number': "021 637 1280",
                'email': "nteboheng.pienaar@westerncape.gov.za",
                'website': None,
                'description': "Trauma & Maternity Obstetric Unit, 24 h service",
                'hours': "24 hours daily",
                'emergency': "Trauma & Maternity services",
                'clinic_type': "public"
            },
            {
                'id': 11,
                'name': "Chapel Street Clinic",
                'address': "Chapel Street, Woodstock, Cape Town, 7925",
                'phone_number': "021 444 1540",
                'email': "clinicmanager.chapel-spencerroad@capetown.gov.za",
                'website': "http://www.westerncape.gov.za",
                'description': "Family planning & general health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 12,
                'name': "Crossroads 1 Clinic",
                'address': "Old Klipfontein Road, Crossroads, Cape Town, 7750",
                'phone_number': "021 444 6435",
                'email': "crossroads1.clinic@capetown.gov.za",
                'website': "http://www.westerncape.gov.za",
                'description': "General community day clinic (TB unit)",
                'hours': "Mon–Fri: 08:00–16:30",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 13,
                'name': "Crossroads Community Day Centre",
                'address': "Govan Mbeki Road, Crossroads, Cape Town",
                'phone_number': "021 385 3031",
                'email': "Conrad.Malgas@westerncape.gov.za",
                'website': "http://www.westerncape.gov.za",
                'description': "Community Day Centre offering primary health care",
                'hours': "Mon–Fri: 07:00–16:30",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 14,
                'name': "Crossroads 2 Clinic",
                'address': "Lansdowne Road, Crossroads, Cape Town",
                'phone_number': "021 386 1113",
                'email': None,
                'website': "http://www.westerncape.gov.za",
                'description': "Satellite clinic in Nyanga health district",
                'hours': None,
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 15,
                'name': "Diep River Clinic",
                'address': "Schaay Road, Diep River, Cape Town, 7800",
                'phone_number': "021 712 9850",
                'email': "diepriver.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 16,
                'name': "Dr Ivan Toms Community Day Centre",
                'address': "Cnr Nqubelani and Umbashe Streets, Ext 6, Mfuleni, Cape Town",
                'phone_number': "021 907 1800",
                'email': "ivan.toms@westerncape.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 08:00–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 17,
                'name': "Driftsands Satellite Clinic",
                'address': "Cnr Xwayi Street and Nkanti Street, Mfuleni, Cape Town",
                'phone_number': "021 907 1800",
                'email': "driftsands@westerncape.gov.za",
                'website': None,
                'description': "Satellite health services",
                'hours': "Mon–Fri: 08:00–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 18,
                'name': "Eastridge Clinic",
                'address': "1st Avenue, Tokin Centre, Eastridge, Mitchell's Plain, Cape Town",
                'phone_number': "021 392 7125/6",
                'email': "eastridge.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 19,
                'name': "Eerste River Clinic",
                'address': "Bobs Way, Eerste River, Cape Town, 7100",
                'phone_number': "021 840 1000",
                'email': "eersteriver.clinic@capetown.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 20,
                'name': "Elsies River Clinic",
                'address': "Halt Road, Elsies River, Cape Town, 7490",
                'phone_number': "021 931 0211",
                'email': "elsiesriver.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 21,
                'name': "Factreton Clinic",
                'address': "Cnr 11th and Factreton Avenues, Factreton, Kensington, Cape Town",
                'phone_number': "021 593 3060/5",
                'email': "factreton.clinic@capetown.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 22,
                'name': "Fagan Street Clinic",
                'address': "Fagan Street, Strand, Cape Town, 7140",
                'phone_number': "021 841 1660",
                'email': "faganstreet.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 24,
                'name': "Gordon's Bay Community Day Centre",
                'address': "Cnr Sir Lowry's Pass Road and Mountainside Boulevard, Gordon's B",
                'phone_number': "021 856 5300",
                'email': "gordonsbay@westerncape.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 25,
                'name': "Gugulethu Clinic",
                'address': "C/o NY1 & NY3, Gugulethu, Cape Town, 7750",
                'phone_number': "021 444 6059",
                'email': "guguletu.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 26,
                'name': "Hanover Park Clinic",
                'address': "Hanover Park Avenue, Hanover Park, Cape Town, 7780",
                'phone_number': "021 692 1251",
                'email': "hanover-park-clinic@capetown.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 27,
                'name': "Harmonie Clinic",
                'address': "Frans Conradie Avenue, Kraaifontein, Cape Town, 7570",
                'phone_number': "021 980 1285",
                'email': "harmonie.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 28,
                'name': "Hazendal (Silvertown) Satellite Clinic",
                'address': "Kuils Street, Silvertown, Kuils River, Cape Town, 7580",
                'phone_number': "021 900 1000",
                'email': "hazendal@westerncape.gov.za",
                'website': None,
                'description': "Satellite health services",
                'hours': "Mon–Fri: 08:00–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 29,
                'name': "Hout Bay Main Road Clinic",
                'address': "Imizamo Yethu, Main Road, Hout Bay, Cape Town, 7806",
                'phone_number': "021 790 3030",
                'email': "houtbay@westerncape.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 30,
                'name': "Ikhwezi Community Day Centre",
                'address': "3 Simon Street, Lwandle, Cape Town, 7140",
                'phone_number': "021 856 5300",
                'email': "ikhwezi@westerncape.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 31,
                'name': "Klip Road Clinic",
                'address': "Cnr Kiewiets and Klip Road, Grassy Park, Cape Town, 7941",
                'phone_number': "021 706 4000",
                'email': "kliproad.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 32,
                'name': "Kuils River Clinic",
                'address': "Carinus Street, Kuils River, Cape Town, 7580",
                'phone_number': "021 900 1000",
                'email': "kuilsrivier.clinic@capetown.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 33,
                'name': "Kuyasa Community Day Centre",
                'address': "Ntazane Road, Kuyasa, Khayelitsha, Cape Town, 7784",
                'phone_number': "021 361 1000",
                'email': "kuyasa@westerncape.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 34,
                'name': "Kuyasa Men's Clinic",
                'address': "Walter Sisulu Road, Kuyasa, Khayelitsha, Cape Town, 7784",
                'phone_number': "021 361 1000",
                'email': "kuyasa.men@westerncape.gov.za",
                'website': None,
                'description': "Men's health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 35,
                'name': "Langa Clinic",
                'address': "Washington Street, Langa, Cape Town, 7455",
                'phone_number': "021 694 1000",
                'email': "langa.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 36,
                'name': "Lansdowne Clinic",
                'address': "Cnr Lansdowne Road and Church Street, Lansdowne, Cape Town, 7780",
                'phone_number': "021 696 1000",
                'email': "lansdowne.clinic@capetown.gov.za",
                'website': None,
                'description': "Community health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            },
            {
                'id': 37,
                'name': "Lavender Hill Clinic",
                'address': "74 Grindal Crescent, Lavender Hill, Cape Town, 7945",
                'phone_number': "021 696 1000",
                'email': "lavenderhill.clinic@capetown.gov.za",
                'website': None,
                'description': "General health services",
                'hours': "Mon–Fri: 07:30–16:00",
                'emergency': None,
                'clinic_type': "public"
            }
        ]

        self.stdout.write(f"Loading {len(clinics_data)} clinics...")
        
        created_count = 0
        updated_count = 0
        
        for clinic_data in clinics_data:
            # Remove the id field for Django create/update operations
            clinic_id = clinic_data.pop('id')
            
            clinic, created = Clinic.objects.update_or_create(
                name=clinic_data['name'],
                defaults=clinic_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created: {clinic.name}")
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"⚠ Updated: {clinic.name}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nLoad complete! Created: {created_count}, Updated: {updated_count}"
            )
        )
        
        # Display final count
        total_clinics = Clinic.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f"Total clinics in database: {total_clinics}")
        )
