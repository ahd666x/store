from django import forms
from django.forms import Select
from .models import Order, Address


class OrderForm(forms.ModelForm):
    address_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Order
        fields = ['shipping_address']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if self.request and self.request.user.is_authenticated:
            self.fields['address_id'].initial = None

    def save(self, commit=True):
        order = super().save(commit=False)
        if self.request:
            order.user = self.request.user
        if commit:
            order.save()
        return order
