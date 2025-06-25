from django import forms
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm, UserCreationForm
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
                messages.success(request, f'Please check your email {to_email} for the password reset link.')
        else:
            if request:
                messages.error(request, f'There was a problem sending the email to {to_email}. Please check the address.')

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text='Required.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text='Required.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        User = get_user_model()
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"A user with username '{username}' already exists.")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"A user with email '{email}' already exists.")
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  #requires email activation
        
        if commit:
            user.save()
        return user
