from django import forms

from .models import Order

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('content',
                  'order_location',
                  'order_status',
                  'order_client_comment',
                  'order_client',
                  'payment_status',
                  'order_cost',
                  'order_courier')
