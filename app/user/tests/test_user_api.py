"""
Tests for the user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status # HTTP status codes



CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """test creating a new user is successful"""
        
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data) # checks that the password is not returned in the response  

    def test_user_with_email_exists(self):
        """Test error returned if user with email already exists"""

        payload = {
            'email': 'test@example.com',
            'password' : 'testpass123',
            'name' : 'Test Name',
            }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 chars"""
            
        payload = {
            'email': 'test@example.com',
            'password' : 'pw',
            'name' : 'Test name',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
            ).exists()
        
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials"""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if invalid credentials are given"""

        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpass' }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_email_not_found(self):
        """Test returns error if email does not exist"""

        payload = {'email': 'test@example.com', 'password': 'pass123'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error"""

        payload = {'email': 'test@example.com', 'password': ''}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""

        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """Tests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
            
        res = self.client.get(ME_URL)
    
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
        self.assertEqual(res.data, {
                'name': self.user.name,
                'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me url"""

        res = self.client.post(ME_URL, {})
    
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""

        payload = {'name': 'Updated Name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)