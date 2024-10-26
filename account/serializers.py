from rest_framework import serializers
from .models import BankAccount, Transaction

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ['id', 'balance', 'is_active', 'user']

        def create(self, validated_data):
            return BankAccount.objects.create(**validated_data)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'amount', 'transaction_type', 'timestamp']