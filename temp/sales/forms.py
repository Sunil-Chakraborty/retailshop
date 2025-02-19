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
