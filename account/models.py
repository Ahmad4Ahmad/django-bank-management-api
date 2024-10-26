from django.db import models
from users.models import User

class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3)  # ISO 4217 currency code
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s account - {self.currency}"

class Transaction(models.Model):
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10)  # deposit, withdraw, transfer
    currency = models.CharField(max_length=3)  # Store currency of the transaction
    timestamp = models.DateTimeField(auto_now_add=True)