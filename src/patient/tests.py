from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from .models import Patient
from .forms import PatientForm


class TestCreatePatientView(TestCase):

    def setUp(self):
        """Set up test data for each test method"""
        # Create a test user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        
        # URL for the create_patient view
        self.create_patient_url = reverse('create_patient')

    def test_create_patient_get_authenticated(self):
        """Test GET request to create_patient when user is authenticated"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Make GET request
        response = self.client.get(self.create_patient_url)
        
        # Assert response is successful
        self.assertEqual(response.status_code, 200)
        
        # Assert correct template is used
        self.assertTemplateUsed(response, "patient/create_patient.html")
        
        # Assert context contains show_navbar
        self.assertIn('show_navbar', response.context)
        self.assertTrue(response.context['show_navbar'])

    def test_create_patient_get_unauthenticated(self):
        """Test GET request to create_patient when user is not authenticated"""
        # Make GET request without logging in
        response = self.client.get(self.create_patient_url)
        
        # Should redirect to login page (302 status code)
        self.assertEqual(response.status_code, 302)
        
        # Should redirect to login URL with next parameter
        self.assertTrue(response['Location'].startswith('/login_user/'))
        self.assertIn('next=', response['Location'])

    def test_create_patient_post_valid_data_no_screening(self):
        """Test POST request with valid patient data and no screening"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Prepare valid form data
        valid_data = {
            'name': 'John',
            'surname': 'Doe',
            'gender': 'M',  # Adjust based on your model choices
            'age': '25',
            'parent_name': 'Jane',
            'parent_surname': 'Doe',
            'parent_id': '1234567890123',
            'parent_contact': '0123456789',
            # No screening_type specified
        }
        
        # Count patients before request
        initial_count = Patient.objects.count()
        
        # Make POST request
        response = self.client.post(self.create_patient_url, data=valid_data)
        
        # Assert redirect (to create_patient page)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('create_patient'))
        
        # Assert patient was created in database
        self.assertEqual(Patient.objects.count(), initial_count + 1)
        
        # Assert patient data is correct
        patient = Patient.objects.get(name='John', surname='Doe')
        self.assertEqual(patient.gender, 'M')
        self.assertEqual(patient.age, '25')  # Age is stored as string
        self.assertEqual(patient.parent_name, 'Jane')
        self.assertEqual(patient.created_by, self.user)
        
        # Follow the redirect and check for success message
        response = self.client.get(reverse('create_patient'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('created successfully' in str(m) for m in messages))

    def test_create_patient_post_with_dental_screening(self):
        """Test POST request with valid data and dental screening"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Prepare valid form data with dental screening
        valid_data = {
            'name': 'Alice',
            'surname': 'Smith',
            'gender': 'F',
            'age': '30',
            'parent_name': 'Bob',
            'parent_surname': 'Smith',
            'parent_id': '9876543210987',
            'parent_contact': '0987654321',
            'screening_type': 'dental'
        }
        
        # Make POST request
        response = self.client.post(self.create_patient_url, data=valid_data)
        
        # Assert patient was created
        patient = Patient.objects.get(name='Alice', surname='Smith')
        self.assertEqual(patient.created_by, self.user)
        
        # Assert redirect to dental screening
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('dental_screening', kwargs={'patient_id': patient.pk})
        self.assertEqual(response['Location'], expected_url)

    def test_create_patient_post_with_dietary_screening(self):
        """Test POST request with valid data and dietary screening"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Prepare valid form data with dietary screening
        valid_data = {
            'name': 'Charlie',
            'surname': 'Brown',
            'gender': 'M',
            'age': '15',
            'parent_name': 'Diana',
            'parent_surname': 'Brown',
            'parent_id': '1122334455667',
            'parent_contact': '0111222333',
            'screening_type': 'dietary'
        }
        
        # Make POST request
        response = self.client.post(self.create_patient_url, data=valid_data)
        
        # Assert patient was created
        patient = Patient.objects.get(name='Charlie', surname='Brown')
        
        # Assert redirect to dietary screening
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('dietary_screening', kwargs={'patient_id': patient.pk})
        self.assertEqual(response['Location'], expected_url)

    def test_create_patient_post_with_both_screenings(self):
        """Test POST request with valid data and both screenings"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Prepare valid form data with both screenings
        valid_data = {
            'name': 'Emma',
            'surname': 'Wilson',
            'gender': 'F',
            'age': '20',
            'parent_name': 'Frank',
            'parent_surname': 'Wilson',
            'parent_id': '9988776655443',
            'parent_contact': '0999888777',
            'screening_type': 'both'
        }
        
        # Make POST request
        response = self.client.post(self.create_patient_url, data=valid_data)
        
        # Assert patient was created
        patient = Patient.objects.get(name='Emma', surname='Wilson')
        
        # Assert redirect to dietary screening with perform_both parameter
        self.assertEqual(response.status_code, 302)
        expected_url = f'/assessments/dietary_screening/{patient.pk}/?perform_both=true'
        self.assertEqual(response['Location'], expected_url)

    def test_create_patient_post_missing_required_fields(self):
        """Test POST request with missing required fields"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Prepare invalid form data (missing required fields)
        invalid_data = {
            'name': 'John',
            'surname': '',  # Missing required field
            'gender': 'M',
            'age': '25',
            'parent_name': '',  # Missing required field
            'parent_surname': 'Doe',
            'parent_id': '1234567890123',
            'parent_contact': '0123456789',
        }
        
        # Count patients before request
        initial_count = Patient.objects.count()
        
        # Make POST request
        response = self.client.post(self.create_patient_url, data=invalid_data)
        
        # Assert response is successful (form with errors is redisplayed)
        self.assertEqual(response.status_code, 200)
        
        # Assert template is rendered
        self.assertTemplateUsed(response, "patient/create_patient.html")
        
        # Assert no patient was created in database
        self.assertEqual(Patient.objects.count(), initial_count)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('All fields are required' in str(m) for m in messages))

    def test_create_patient_post_empty_data(self):
        """Test POST request with completely empty data"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Make POST request with empty data
        response = self.client.post(self.create_patient_url, data={})
        
        # Assert response is successful (form with errors is redisplayed)
        self.assertEqual(response.status_code, 200)
        
        # Assert template is rendered
        self.assertTemplateUsed(response, "patient/create_patient.html")
        
        # Assert no patient was created
        self.assertEqual(Patient.objects.count(), 0)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('All fields are required' in str(m) for m in messages))

    def test_create_patient_post_exception_handling(self):
        """Test POST request exception handling"""
        # Log in the test user
        self.client.login(username='testuser', password='testpass123')
        
        # Test case: try to create patient with invalid integer conversion
        # by passing non-numeric age that might cause issues in processing
        potentially_problematic_data = {
            'name': 'Test',
            'surname': 'User',
            'gender': 'M',
            'age': 'invalid_age_that_might_cause_issues',  # This could cause issues if view tries to convert
            'parent_name': 'Parent',
            'parent_surname': 'User',
            'parent_id': '1234567890123',
            'parent_contact': '0123456789',
        }
        
        # Make POST request - view should handle any exception gracefully
        response = self.client.post(self.create_patient_url, data=potentially_problematic_data)
        
        # The view should either:
        # 1. Handle the exception and show error (200 with template)
        # 2. Successfully create the patient if no actual exception occurs (302 redirect)
        self.assertIn(response.status_code, [200, 302])
        
        # If it's a successful creation (302), the patient should exist
        # If it's an error (200), patient should not exist
        if response.status_code == 302:
            # Success case - patient was created
            self.assertTrue(Patient.objects.filter(name='Test', surname='User').exists())
        else:
            # Error case - patient should not be created and template should be shown
            self.assertTemplateUsed(response, "patient/create_patient.html")
            self.assertFalse(Patient.objects.filter(name='Test', surname='User').exists())

    def test_create_patient_user_association(self):
        """Test that patients are correctly associated with the logged-in user"""
        # Create two different users
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # Log in first user and create patient
        self.client.login(username='testuser', password='testpass123')
        
        valid_data = {
            'name': 'User1Patient',
            'surname': 'Test',
            'gender': 'M',
            'age': '25',
            'parent_name': 'Parent1',
            'parent_surname': 'Test',
            'parent_id': '1111111111111',
            'parent_contact': '0111111111',
        }
        
        self.client.post(self.create_patient_url, data=valid_data)
        
        # Log in second user and create patient
        self.client.login(username='testuser2', password='testpass123')
        
        valid_data2 = {
            'name': 'User2Patient',
            'surname': 'Test',
            'gender': 'F',
            'age': '30',
            'parent_name': 'Parent2',
            'parent_surname': 'Test',
            'parent_id': '2222222222222',
            'parent_contact': '0222222222',
        }
        
        self.client.post(self.create_patient_url, data=valid_data2)
        
        # Assert patients are associated with correct users
        user1_patients = Patient.objects.filter(created_by=self.user)
        user2_patients = Patient.objects.filter(created_by=user2)
        
        self.assertEqual(user1_patients.count(), 1)
        self.assertEqual(user2_patients.count(), 1)
        
        # Get the actual patient objects and check names
        user1_patient = user1_patients.first()
        user2_patient = user2_patients.first()
        
        self.assertIsNotNone(user1_patient)
        self.assertIsNotNone(user2_patient)
        
        # More defensive attribute access to satisfy linter
        self.assertEqual(getattr(user1_patient, 'name', None), 'User1Patient')
        self.assertEqual(getattr(user2_patient, 'name', None), 'User2Patient')

class TestPatientListView(TestCase):

    def setUp(self):
        """Set up test data for the test method"""

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.client = Client()

        self.patient_list_url = reverse('patient_list')
        
        # Create test patients for user1
        self.patient1 = Patient.objects.create(
            name='John',
            surname='Doe',
            gender='M',
            age='25',
            parent_name='Jane',
            parent_surname='Doe',
            parent_id='1234567890123',
            parent_contact='0123456789',
            created_by=self.user
        )
        
        self.patient2 = Patient.objects.create(
            name='Alice',
            surname='Smith',
            gender='F',
            age='30',
            parent_name='Bob',
            parent_surname='Smith',
            parent_id='9876543210987',
            parent_contact='0987654321',
            created_by=self.user
        )
        
        # Create patient for user2 (should not appear in user1's list)
        self.patient3 = Patient.objects.create(
            name='Charlie',
            surname='Brown',
            gender='M',
            age='15',
            parent_name='Diana',
            parent_surname='Brown',
            parent_id='1122334455667',
            parent_contact='0111222333',
            created_by=self.user2
        )

    def test_patient_list_view_get_authenticated(self):
        """Test GET request to patient_list_view when user is authenticated"""

        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(self.patient_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "patient/patient_list.html")
        
        # Check context variables
        self.assertIn('patients', response.context)
        self.assertIn('show_navbar', response.context)
        self.assertIn('total_patients', response.context)
        self.assertTrue(response.context['show_navbar'])
        
        # Check that only user's patients are shown (2 patients for user1)
        self.assertEqual(response.context['total_patients'], 2)
        
        # Check that the correct patients are in the context
        patients = response.context['patients']
        patient_names = [p.name for p in patients]
        self.assertIn('John', patient_names)
        self.assertIn('Alice', patient_names)
        self.assertNotIn('Charlie', patient_names)  # User2's patient should not appear

    def test_patient_list_view_get_unauthenticated(self):
        """Test GET request to patient_list_view when user is not authenticated"""
        
        response = self.client.get(self.patient_list_url)
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login_user/', response['Location'])

    def test_patient_list_view_search_by_name(self):
        """Test search functionality by patient name"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Search for "John"
        response = self.client.get(self.patient_list_url, {'search': 'John'})
        
        self.assertEqual(response.status_code, 200)
        patients = response.context['patients']
        
        # Should return only John
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0].name, 'John')
        
        # Check search query is preserved in context
        self.assertEqual(response.context['search_query'], 'John')

    def test_patient_list_view_search_by_surname(self):
        """Test search functionality by patient surname"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Search for "Smith"
        response = self.client.get(self.patient_list_url, {'search': 'Smith'})
        
        self.assertEqual(response.status_code, 200)
        patients = response.context['patients']
        
        # Should return only Alice Smith
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0].surname, 'Smith')

    def test_patient_list_view_search_by_parent_id(self):
        """Test search functionality by parent ID"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Search for parent ID
        response = self.client.get(self.patient_list_url, {'search': '1234567890123'})
        
        self.assertEqual(response.status_code, 200)
        patients = response.context['patients']
        
        # Should return John (who has this parent ID)
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0].parent_id, '1234567890123')

    def test_patient_list_view_search_by_parent_contact(self):
        """Test search functionality by parent contact"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Search for parent contact
        response = self.client.get(self.patient_list_url, {'search': '0987654321'})
        
        self.assertEqual(response.status_code, 200)
        patients = response.context['patients']
        
        # Should return Alice (who has this parent contact)
        self.assertEqual(len(patients), 1)
        self.assertEqual(patients[0].parent_contact, '0987654321')

    def test_patient_list_view_search_case_insensitive(self):
        """Test that search is case insensitive"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Search with different cases
        search_terms = ['john', 'JOHN', 'John', 'jOhN']
        
        for term in search_terms:
            response = self.client.get(self.patient_list_url, {'search': term})
            patients = response.context['patients']
            
            # Should always return John regardless of case
            self.assertEqual(len(patients), 1)
            self.assertEqual(patients[0].name, 'John')

    def test_patient_list_view_search_no_results(self):
        """Test search with no matching results"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Search for non-existent patient
        response = self.client.get(self.patient_list_url, {'search': 'NonExistent'})
        
        self.assertEqual(response.status_code, 200)
        patients = response.context['patients']
        
        # Should return no patients
        self.assertEqual(len(patients), 0)
        self.assertEqual(response.context['total_patients'], 0)

    def test_patient_list_view_search_empty_string(self):
        """Test search with empty string returns all patients"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Search with empty string
        response = self.client.get(self.patient_list_url, {'search': ''})
        
        self.assertEqual(response.status_code, 200)
        patients = response.context['patients']
        
        # Should return all user's patients (2)
        self.assertEqual(len(patients), 2)
        self.assertEqual(response.context['search_query'], '')

    def test_patient_list_view_search_whitespace_only(self):
        """Test search with whitespace only is handled correctly"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Search with spaces only
        response = self.client.get(self.patient_list_url, {'search': '   '})
        
        self.assertEqual(response.status_code, 200)
        patients = response.context['patients']
        
        # Should return all patients (whitespace is stripped)
        self.assertEqual(len(patients), 2)
        self.assertEqual(response.context['search_query'], '')

    def test_patient_list_view_pagination_context(self):
        """Test pagination context variables"""
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.patient_list_url)
        
        # Check pagination context
        self.assertIn('page_obj', response.context)
        self.assertIn('is_paginated', response.context)
        
        # With only 2 patients, should not be paginated (page size is 25)
        self.assertFalse(response.context['is_paginated'])

    def test_patient_list_view_pagination_with_many_patients(self):
        """Test pagination when there are many patients"""
        
        self.client.login(username='testuser', password='testpass123')
        
        # Create 30 more patients to test pagination (total 32, page size is 25)
        for i in range(30):
            Patient.objects.create(
                name=f'Patient{i}',
                surname=f'Test{i}',
                gender='M' if i % 2 == 0 else 'F',
                age=str(20 + i % 10),
                parent_name=f'Parent{i}',
                parent_surname=f'TestParent{i}',
                parent_id=f'ID{i:013d}',
                parent_contact=f'0{i:09d}',
                created_by=self.user
            )
        
        # Test first page
        response = self.client.get(self.patient_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['patients']), 25)  # Page size
        self.assertEqual(response.context['total_patients'], 32)  # Total patients
        
        # Test second page
        response = self.client.get(self.patient_list_url, {'page': 2})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['patients']), 7)  # Remaining patients

    def test_patient_list_view_ordering(self):
        """Test that patients are ordered by most recent (by ID descending)"""
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.patient_list_url)
        
        patients = list(response.context['patients'])
        
        # Should be ordered by ID descending (most recent first)
        # patient2 was created after patient1, so should come first
        self.assertEqual(patients[0].pk, self.patient2.pk)
        self.assertEqual(patients[1].pk, self.patient1.pk)

    def test_patient_list_view_user_isolation(self):
        """Test that users only see their own patients"""
        
        # Test user1 sees only their patients
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.patient_list_url)
        
        patients = response.context['patients']
        patient_ids = [p.pk for p in patients]
        
        # Should see patient1 and patient2, but not patient3
        self.assertIn(self.patient1.pk, patient_ids)
        self.assertIn(self.patient2.pk, patient_ids)
        self.assertNotIn(self.patient3.pk, patient_ids)
        
        # Test user2 sees only their patients
        self.client.login(username='testuser2', password='testpass123')
        response = self.client.get(self.patient_list_url)
        
        patients = response.context['patients']
        patient_ids = [p.pk for p in patients]
        
        # Should see only patient3
        self.assertNotIn(self.patient1.pk, patient_ids)
        self.assertNotIn(self.patient2.pk, patient_ids)
        self.assertIn(self.patient3.pk, patient_ids)

    def test_patient_list_view_no_patients(self):
        """Test patient list view when user has no patients"""
        
        # Create new user with no patients
        user3 = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        self.client.login(username='newuser', password='testpass123')
        response = self.client.get(self.patient_list_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "patient/patient_list.html")
        
        # Should have empty patient list
        self.assertEqual(len(response.context['patients']), 0)
        self.assertEqual(response.context['total_patients'], 0)
        self.assertFalse(response.context['is_paginated'])
