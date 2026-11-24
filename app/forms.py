from django import forms
from .models import Expense


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date']

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter expense name'
            }),

            'amount': forms.NumberInput(attrs={
                'placeholder': 'Enter amount'
            }),

            'date': forms.DateInput(attrs={
                'type': 'date'
            }),
        }