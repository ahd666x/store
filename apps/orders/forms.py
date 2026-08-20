from django import forms
from .models import Order
from apps.cart.models import Cart


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
            cart = Cart.objects.get(user=self.request.user)
            order.total_amount = cart.total_price
            order.final_amount = order.total_amount
        if commit:
            order.save()
        return order
