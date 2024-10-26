from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Loan, User, BankAccount
from rest_framework_simplejwt.tokens import RefreshToken

class BankTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )

        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token.access_token))
        self.create_account_url = reverse('account-create')
        self.account = BankAccount.objects.create(
            user=self.user,
            balance=1000,
            currency='ILS'
        )
        
        self.loan_url = reverse('grant-loan')
        self.loan = Loan.objects.create(user=self.user, amount=20000)

    def test_grant_loan(self):
        data = {'amount': 30000}  # Valid loan amount
        response = self.client.post(self.loan_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 2)  # One existing + new loan

    def test_grant_loan_exceed_limit(self):
        data = {'amount': 60000}  # Exceeds max loan amount
        response = self.client.post(self.loan_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_repay_loan(self):
        loan_repayment_url = reverse('repay-loan', args=[self.loan.id])
        data = {'amount': 5000}  # Repayment amount
        response = self.client.post(loan_repayment_url, data, format='json')
        self.loan.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.loan.amount, 15000)

    def test_repay_loan_exceed_amount(self):
        loan_repayment_url = reverse('repay-loan', args=[self.loan.id])
        data = {'amount': 25000}  # Exceeds remaining loan amount
        response = self.client.post(loan_repayment_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_customer_loans(self):
        url = reverse('get-loans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should return the existing loan