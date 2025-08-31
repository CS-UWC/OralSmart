from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from userprofile.models import Profile

class Command(BaseCommand):
    help = 'Create test users for E2E testing'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create test user for authentication
        username = 'testuser123'
        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()
            
        user = User.objects.create_user(
            username=username,
            email='testuser@example.com',
            password='ComplexPass123!',
            first_name='Test',
            last_name='User',
            is_active=True  # Make user active for testing
        )
        
        # Create associated profile
        Profile.objects.create(
            user=user,
            profession='Dentist',
            health_professional_body='ADA',
            reg_num='TEST123',
            email=user.email
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created test user: {username}')
        )
        
        # Create staff user for admin testing
        staff_username = 'staffuser123'
        if User.objects.filter(username=staff_username).exists():
            User.objects.filter(username=staff_username).delete()
            
        staff_user = User.objects.create_user(
            username=staff_username,
            email='staffuser@example.com',
            password='StaffPass123!',
            first_name='Staff',
            last_name='User',
            is_active=True,
            is_staff=True
        )
        
        Profile.objects.create(
            user=staff_user,
            profession='Admin',
            health_professional_body='Admin',
            reg_num='STAFF123',
            email=staff_user.email
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created staff user: {staff_username}')
        )
