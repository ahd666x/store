from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        order = super().save(commit=False)
        if self.request:
            order.user = self.request.user
        if commit:
            order.save()
        return order
