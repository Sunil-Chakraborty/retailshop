from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

class CustomerRegistrationForm(UserCreationForm):
    mobile_number = forms.CharField(max_length=15)
    name = forms.CharField(max_length=255)
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Customer
        fields = ['mobile_number', 'name', 'address']


class CustomerForm(forms.ModelForm):
    mobile_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your 10-digit mobile number'}),
        error_messages={'required': 'Mobile number is required.', 'invalid': 'Invalid mobile number.'}
    )

    class Meta:
        model = Customer
        fields = [ 'mobile_number', 'name', 'address']

    