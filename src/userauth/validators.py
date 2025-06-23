import re
from django.core.exceptions import ValidationError

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if (not re.findall('[A-Z]', password) or
            not re.findall('[a-z]', password) or
            not re.findall('[0-9]', password) or
            not re.findall('[!@#$%^&*(),.?":{}|<>]', password)):
            raise ValidationError(
                "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."
            )
    def get_help_text(self):
        return "Your password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."