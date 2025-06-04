from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from .middleware import SecurityHeadersMiddleware

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('security:register')
        self.login_url = reverse('security:token_obtain_pair')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'password2': 'testpass123',
            'email': 'test@example.com',
            'role': 'merchant'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        # Create user first
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='merchant'
        )
        
        # Attempt login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class PermissionsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.merchant = User.objects.create_user(
            username='merchant',
            password='merchant123',
            role='merchant'
        )
        self.user = User.objects.create_user(
            username='user',
            password='user123',
            role='user'
        )
        self.users_url = reverse('security:user-list')

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def test_admin_can_list_users(self):
        tokens = self.get_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_merchant_cannot_list_users(self):
        tokens = self.get_tokens_for_user(self.merchant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SecurityHeadersMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware(lambda r: HttpResponse())

    def test_security_headers_added(self):
        request = self.factory.get('/')
        response = self.middleware(request)
        
        # Test that all security headers are present
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        self.assertEqual(response['Strict-Transport-Security'], 'max-age=31536000; includeSubDomains')
        self.assertEqual(response['Content-Security-Policy'], "default-src 'self'")
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')
        self.assertEqual(response['Cache-Control'], 'no-store, no-cache, must-revalidate, max-age=0')
        self.assertEqual(response['Pragma'], 'no-cache')

    def test_rate_limiting(self):
        request = self.factory.get('/')
        request.user = User.objects.create_user(username='testuser', password='testpass')
        
        # First request should pass
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        
        # Make 61 requests (exceeding the per-minute limit)
        for _ in range(61):
            response = self.middleware(request)
        
        # The last request should be forbidden
        self.assertEqual(response.status_code, 403)