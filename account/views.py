from rest_framework import generics, status
from rest_framework.response import Response
from account.utils import convert_currency
from .models import Transaction, BankAccount
from .serializers import BankAccountSerializer, TransactionSerializer
from .mixins import AccountMixin
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from drf_spectacular.utils import extend_schema

FEE_PERCENTAGE = Decimal('0.01') # Example fee percentage

@extend_schema(tags=['Bank account'])
class CreateAccountView(generics.CreateAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can create accounts

    def perform_create(self, serializer):
        # Automatically set the user to the currently authenticated user
        serializer.save(user=self.request.user)

@extend_schema(tags=['Bank account'])
class DepositView(AccountMixin, generics.UpdateAPIView):
    serializer_class = TransactionSerializer

    def post(self, request, pk):
        account = self.get_account(pk)
        amount = Decimal(request.data.get('amount', 0))
        currency = request.data.get('currency', account.currency)  # Use account currency if not provided
        if amount <= 0:
            raise ValidationError("Deposit amount must be greater than zero.")
        
        fee = amount * FEE_PERCENTAGE
        net_amount = amount - fee  # Amount after deducting the fee
        if net_amount <= 0:
            raise ValidationError("Deposit amount after fee must be greater than zero.")

        if currency != account.currency:
            net_amount = convert_currency(net_amount, currency, account.currency)

        account.balance += net_amount
        account.save()

        # Create the transaction record
        Transaction.objects.create(
            account=account,
            amount=net_amount,
            transaction_type='deposit',
            currency=account.currency
        )

        return Response({'balance': account.balance, 'message': 'Deposit successful!'})

@extend_schema(tags=['Bank account'])
class WithdrawView(AccountMixin, generics.UpdateAPIView):
    serializer_class = TransactionSerializer

    def post(self, request, pk):
        account = self.get_account(pk)
        amount = Decimal(request.data.get('amount', 0))
        currency = request.data.get('currency', account.currency)  # Use account currency if not provided
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be greater than zero.")
        
        fee = amount * FEE_PERCENTAGE
        net_amount = amount + fee  # Amount after deducting the fee
        if net_amount <= 0:
            raise ValidationError("Withdrawal amount after fee must be greater than zero.")

        if currency != account.currency:
            net_amount = convert_currency(net_amount, currency, account.currency)

        if account.balance - net_amount < -1000:  # Change -1000 to your desired overdraft limit
            raise ValidationError("Insufficient funds for withdrawal.")

        account.balance -= net_amount
        account.save()
        Transaction.objects.create(account=account, amount=net_amount, transaction_type='withdraw', currency=account.currency)
        return Response({'balance': account.balance})

@extend_schema(tags=['Bank account'])
class TransferView(AccountMixin, generics.GenericAPIView):
    def post(self, request):
        from_account_id = request.data.get('from_account_id')
        to_account_id = request.data.get('to_account_id')
        amount = Decimal(request.data.get('amount', 0))
        currency = request.data.get('currency')  # Specify the currency for the transfer

        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)

        if amount <= 0:
            raise ValidationError("Transfer amount must be greater than zero.")
        
        fee = amount * FEE_PERCENTAGE
        net_amount = amount + fee
        if net_amount <= 0:
            raise ValidationError("Transfer amount after fee must be greater than zero.")

        if currency != from_account.currency:
            net_amount = convert_currency(net_amount, currency, from_account.currency)

        if from_account.balance - amount < -1000:  # Change -1000 to your desired overdraft limit
            raise ValidationError("Insufficient funds for transfer.")

        from_account.balance -= net_amount
        to_account.balance += amount

        from_account.save()
        to_account.save()

        Transaction.objects.create(account=from_account, amount=net_amount, transaction_type='transfer', currency=from_account.currency)
        Transaction.objects.create(account=to_account, amount=amount, transaction_type='transfer', currency=to_account.currency)

        return Response({'from_balance': from_account.balance, 'to_balance': to_account.balance})

@extend_schema(tags=['Bank account']) 
class SuspendAccountView(AccountMixin, generics.UpdateAPIView):
    serializer_class = BankAccountSerializer

    def post(self, request, pk):
        account = self.get_account(pk)
        account.is_active = False
        account.save()
        return Response({'detail': 'Account suspended'})

@extend_schema(tags=['Bank account']) 
class CloseAccountView(generics.DestroyAPIView):
    queryset = BankAccount.objects.all()

    def destroy(self, request, pk):
        account = self.get_object()
        if account.balance < 0:
            raise ValidationError("Cannot close account with a negative balance.")
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(tags=['Bank account'])    
class UserTransactionsView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the user's bank accounts and then filter transactions
        user_accounts = BankAccount.objects.filter(user=self.request.user)
        return Transaction.objects.filter(account__in=user_accounts).order_by('-timestamp')