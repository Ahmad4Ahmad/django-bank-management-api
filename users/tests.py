from django.urls import reverse
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

class UserTests(APITestCase):
    def setUp(self):
        self.create_url = reverse('user-create')
        self.login_url = reverse('user-login')
        self.logout_url = reverse('user-logout')
        self.user = None
        self.token = None

    def get_auth_token(self):
        if self.user is None:
            self.test_create_user()  # Create a user if not already created

        url = reverse("token_obtain_pair")
        response = self.client.post(url, {
            'email': self.user.email,
            'password': "newpassword"
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.access_token = response.data['access']
        self.refresh_token = response.data['refresh']
        return response.data  # Return only the access token

    def test_create_user(self):
        url = reverse('user-create')
        data = {
            'password': 'newpassword',
            'email': 'new@example.com',
            'first_name': 'John',
            'last_name': 'Doe'   
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(email='new@example.com')
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.check_password(data['password']))
        self.user = User.objects.get(email=data['email'])

    def test_create_user_welcome_email(self):
        url = reverse('user-create')
        data = {
            'password': 'newpassword',
            'email': 'new@example.com'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that one message has been sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Welcome to Our Bank!')
        self.assertIn('Welcome, new@example.com!', mail.outbox[0].body)

    def test_update_user(self):
        if self.user is None:
            self.test_create_user()  # Create a user if not already created

        url = reverse('user-update', args=[self.user.id])
        data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }

        # Call get_auth_token to ensure the token is retrieved
        self.token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.patch(url, data, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_create_user_with_duplicate_email(self):
        # First, create an initial user
        initial_data = {
            'password': 'initialpassword',
            'email': 'duplicate@example.com',
            'first_name': 'Initial',
            'last_name': 'User'
        }

        response = self.client.post(self.create_url, initial_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Now, try to create a user with the same email
        duplicate_data = {
            'password': 'anotherpassword',
            'email': 'duplicate@example.com',  # Same email as initial user
            'first_name': 'Duplicate',
            'last_name': 'User'
        }

        response = self.client.post(self.create_url, duplicate_data, format='json')
        
        # Check that the response indicates a conflict
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Or HTTP_409_CONFLICT
        # Check for error message
        self.assertIn('email', response.data['errors'])
        self.assertIn('user with this email address already exists.', str(response.data['errors']['email'][0]))  # Check the specific error message

    def test_delete_user(self):
        if self.user is None:
            self.test_create_user()

        url = reverse('user-delete', args=[self.user.id])
        self.token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_login_user(self):
        if self.user is None:
            self.test_create_user()

        response = self.client.post(self.login_url, {
            'email': 'new@example.com',
            'password': 'newpassword'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_logout_user(self):
        self.token = self.get_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post(self.logout_url, {'refresh': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    def test_login_with_invalid_credentials(self):
        if self.user is None:
            self.test_create_user()

        response = self.client.post(self.login_url, {
            'email': self.user.email,
            'password': 'wrongpassword'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Expect a 400 error
        self.assertIn('non_field_errors', response.data)  # Check for error key
        self.assertIn('Invalid email or password.', response.data['non_field_errors'])  # Check for specific error message