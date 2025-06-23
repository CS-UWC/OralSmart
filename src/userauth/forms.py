from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages

class CustomSetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        model = get_user_model()

        if not model.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError('No User is associated with this email address.')
        return email

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Custom email sending logic, similar to activateEmail.
        """
        request = context.get('request')

        subject = render_to_string(subject_template_name, context).strip()
        message = render_to_string(email_template_name, context)
        email = EmailMessage(subject, message, to=[to_email])

        if email.send():
            if request:
                messages.success(request, f'Please check your email <b>{to_email}</b> for the password reset link.')
        else:
            if request:
                messages.error(request, f'There was a problem sending the email to {to_email}. Please check the address.')
