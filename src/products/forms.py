from django import forms
from .models import Product

class ProductForm(forms.ModelForm):

    # <<begin variables - These variables override the normal model variables and add basic validation
    title = forms.CharField()
    description = forms.CharField()
    price = forms.DecimalField()
    summary = forms.CharField(required=True, widget=forms.Textarea(
        attrs={
            'placeholder': "Your summary",
            'rows': 15,
            'cols': 140,
        }
    ))
    featured = forms.BooleanField()
    # end variables>>
    
    class Meta:
        
        model = Product
        fields = [
            'title',
            'description',
            'price',
            'summary',
            'featured',
        ]

    def clean_title(self, *args, **kwargs): #Validates title by checking if a certain character or word is in the title

        title = self.cleaned_data.get('title')

        if title is not None and "A" not in title:
            raise forms.ValidationError('This is not a valid title')
        else:
            return title



# class RawProductForm(forms.Form):

#     title = forms.CharField()
#     description = forms.CharField()
#     price = forms.DecimalField()
#     summary = forms.CharField(required=True, widget=forms.Textarea(
#         attrs={
#             'placeholder': "Your summary",
#             'rows': 15,
#             'cols': 140,
#         }
#     ))
#     featured = forms.BooleanField()