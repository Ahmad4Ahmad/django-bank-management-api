from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Loan
from .serializers import LoanSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Bank'])
class GrantLoanView(generics.CreateAPIView):
    serializer_class = LoanSerializer

    def post(self, request):
        bank_balance = 10000000  # Starting balance (replace with actual balance retrieval)
        amount = request.data.get('amount')
        if amount > 50000 or bank_balance < amount:
            return Response({'detail': 'Loan request denied'}, status=status.HTTP_400_BAD_REQUEST)
        
        loan = Loan.objects.create(user=request.user, amount=amount)
        return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)

@extend_schema(tags=['Bank'])
class LoanRepaymentView(generics.UpdateAPIView):
    serializer_class = LoanSerializer

    def post(self, request, pk):
        try:
            loan = Loan.objects.get(pk=pk, user=request.user)
        except Loan.DoesNotExist:
            raise NotFound("Loan not found or you do not have permission to access it.")

        repayment_amount = request.data.get('amount')
        if repayment_amount <= 0:
            return Response({'detail': 'Repayment amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        if repayment_amount > loan.amount:
            return Response({'detail': 'Repayment amount exceeds loan balance.'}, status=status.HTTP_400_BAD_REQUEST)

        loan.amount -= repayment_amount
        loan.save()

        return Response(LoanSerializer(loan).data)

@extend_schema(tags=['Bank'])
class GetCustomerLoansView(generics.ListAPIView):
    serializer_class = LoanSerializer

    def get_queryset(self):
        return Loan.objects.filter(user=self.request.user)