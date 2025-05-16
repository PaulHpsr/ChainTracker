from django import forms
from .models import Wallet


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['crypto_type', 'address', 'label']
        widgets = {
            'crypto_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse du portefeuille'}),
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom ou description'}),
        }
