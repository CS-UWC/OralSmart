"""
Utility functions for user authentication and validation.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

def check_username_exists(username):
    """
    Check if a username already exists in the database.
    
    Args:
        username (str): The username to check
        
    Returns:
        bool: True if username exists, False otherwise
    """
    return User.objects.filter(username=username).exists()

def check_email_exists(email):
    """
    Check if an email already exists in the database.
    
    Args:
        email (str): The email to check
        
    Returns:
        bool: True if email exists, False otherwise
    """
    return User.objects.filter(email=email).exists()

def validate_user_uniqueness(username, email):
    """
    Validate that both username and email are unique.
    
    Args:
        username (str): The username to validate
        email (str): The email to validate
        
    Returns:
        dict: Dictionary with validation results
    
    Raises:
        ValidationError: If username or email already exists
    """
    errors = {}
    
    if check_username_exists(username):
        errors['username'] = f"A user with username '{username}' already exists."
    
    if check_email_exists(email):
        errors['email'] = f"A user with email '{email}' already exists."
    
    if errors:
        raise ValidationError(errors)
    
    return {'valid': True}

def get_user_by_username_or_email(identifier):
    """
    Get user by username or email.
    
    Args:
        identifier (str): Username or email
        
    Returns:
        User or None: User object if found, None otherwise
    """
    try:
        # Try to get by email first
        if '@' in identifier:
            return User.objects.get(email=identifier)
        else:
            return User.objects.get(username=identifier)
    except User.DoesNotExist:
        return None

def create_user_safely(username, email, password, **extra_fields):
    """
    Create a user with validation checks.
    
    Args:
        username (str): The username
        email (str): The email
        password (str): The password
        **extra_fields: Additional fields for the user
        
    Returns:
        User: The created user object
        
    Raises:
        ValidationError: If username or email already exists
    """
    # Validate uniqueness first
    validate_user_uniqueness(username, email)
    
    # Create the user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        **extra_fields
    )
    
    return user
