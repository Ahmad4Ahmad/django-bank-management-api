from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import BankAccount, User, Transaction
from rest_framework_simplejwt.tokens import RefreshToken

class AccountTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword'
        )

        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.token.access_token))
        self.create_account_url = reverse('account-create')
        self.account = BankAccount.objects.create(
            user = self.user,
            balance = 500,  # Initial balance
            currency = 'ILS'
        )

        Transaction.objects.create(account=self.account, amount=100.00, transaction_type='deposit', currency='ILS')
        Transaction.objects.create(account=self.account, amount=50.00, transaction_type='withdraw', currency='ILS')

    def test_create_account(self):
        data = {
            'user': self.user.id,  # Pass the user ID
            'balance': 500,
            'currency': 'ILS',
            'is_active': True
        }

        response = self.client.post(self.create_account_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BankAccount.objects.count(), 2)

    def test_deposit(self):
        url = reverse('account-deposit', args=[self.account.id])
        data = {'amount': 200, 'currency': 'ILS'}
        response = self.client.post(url, data, format='json')
        self.account.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.account.balance, 698.00)  # Assuming the initial balance was 500

        # Check if the transaction was created
        transaction = Transaction.objects.last()  # Get the most recent transaction
        self.assertIsNotNone(transaction)  # Ensure a transaction exists
        self.assertEqual(transaction.transaction_type, 'deposit')
        self.assertEqual(transaction.currency, 'ILS')
        self.assertEqual(transaction.account, self.account)

    def test_withdraw(self):
        url = reverse('account-withdraw', args=[self.account.id])
        data = {'amount': 300}
        response = self.client.post(url, data, format='json')
        self.account.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.account.balance, 197.00)

    def test_withdraw_insufficient_funds(self):
        url = reverse('account-withdraw', args=[self.account.id])
        data = {'amount': 2000}  # More than balance
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_suspend_account(self):
        url = reverse('account-suspend', args=[self.account.id])
        response = self.client.post(url)
        self.account.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.account.is_active)

    def test_close_account(self):
        url = reverse('account-close', args=[self.account.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BankAccount.objects.count(), 0)

    # test transfer between two bank accounts
    def test_transfer(self):
        recipient = User.objects.create_user(
            username = 'recipientuser',
            password = 'recipientpassword',
            email = 'recipient@example.com'
        )

        recipient_account = BankAccount.objects.create(
            user = recipient,
            balance = 500,
            currency = 'ILS'
        )

        transfer_url = reverse('account-transfer')
        data = {
            'from_account_id': self.account.id,
            'to_account_id': recipient_account.id,
            'amount': 200,
            'currency': "ILS"
        }

        response = self.client.post(transfer_url, data, format='json')
        self.account.refresh_from_db()
        recipient_account.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.account.balance, 298.00)
        self.assertEqual(recipient_account.balance, 700)

    def test_transfer_insufficient_funds(self):
        recipient = User.objects.create_user(
            username='recipientuser',
            password='recipientpassword',
            email='recipient@example.com'
        )

        recipient_account = BankAccount.objects.create(
            user=recipient,
            balance=500,
            currency='ILS'
        )

        transfer_url = reverse('account-transfer')
        data = {
            'from_account_id': self.account.id,
            'to_account_id': recipient_account.id,
            'amount': 2000,  # More than balance
            'currency': 'ILS'
        }

        response = self.client.post(transfer_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_transactions(self):
        url = reverse('user-transactions')
        response = self.client.get(url)
        
        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response data contains the correct transactions
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['transaction_type'], 'deposit')
        self.assertEqual(response.data[1]['transaction_type'], 'withdraw')