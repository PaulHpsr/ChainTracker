from django.db import models
from django.contrib.auth.models import User


class Wallet(models.Model):
    CRYPTO_CHOICES = [
        ('ethereum', 'Ethereum'),
        ('bnb', 'BNB'),
        ('polygon', 'Polygon'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wallets")
    crypto_type = models.CharField(
        max_length=10, choices=CRYPTO_CHOICES, default='ethereum')
    # adresse ETH/BNB/Polygon (même format)
    address = models.CharField(max_length=42, unique=True)
    label = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.label if self.label else self.address
