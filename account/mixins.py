from rest_framework.exceptions import ValidationError
from .models import BankAccount

class AccountMixin:
    def get_account(self, pk):
        try:
            return BankAccount.objects.get(pk=pk)
        except BankAccount.DoesNotExist:
            raise ValidationError("Account not found.")