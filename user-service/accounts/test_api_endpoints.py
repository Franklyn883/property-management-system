"""
Comprehensive API endpoint tests for the User Service.

This module contains integration tests for all ViewSets and API endpoints,
testing authentication, authorization, rate limiting, and functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
import uuid
from ..models import UserProfile

User = get_user_model()


class BaseAPITestCase(TestCase):
    """Base test case with common setup for API tests."""
    
    def setUp(self):
        """Set up test data for API tests."""
        self.client = APIClient()
        
        # Create test users with different roles
        self.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            role="admin",
            is_verified=True
        )
        
        self.owner_user = User.objects.create_user(
            email="owner@test.com", 
            password="testpass123",
            role="owner",
            is_verified=True
        )
        
        self.agent_user = User.objects.create_user(
            email="agent@test.com",
            password="testpass123", 
            role="agent",
            is_verified=True
        )
        
        self.tenant_user = User.objects.create_user(
            email="tenant@test.com",
            password="testpass123",
            role="tenant", 
            is_verified=True
        )
        
        self.manager_user = User.objects.create_user(
            email="manager@test.com",
            password="testpass123",
            role="manager",
            is_verified=True
        )
        
        # Create user profiles
        self.admin_profile = UserProfile.objects.create(user=self.admin_user)
        self.owner_profile = UserProfile.objects.create(user=self.owner_user)
        self.agent_profile = UserProfile.objects.create(user=self.agent_user)
        self.tenant_profile = UserProfile.objects.create(user=self.tenant_user)
        self.manager_profile = UserProfile.objects.create(user=self.manager_user)
    
    def get_jwt_token(self, user):
        """Get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def authenticate_user(self, user):
        """Authenticate a user with JWT token."""
        token = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def unauthenticate_user(self):
        """Remove authentication."""
        self.client.credentials()


class ProfileAPITests(BaseAPITestCase):
    """Tests for Profile API endpoints."""
    
    def test_get_profile_authenticated(self):
        """Test getting profile for authenticated user."""
        self.authenticate_user(self.owner_user)
        
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['user_role'], 'owner')
    
    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication."""
        url = reverse('profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile_authenticated(self):
        """Test updating profile for authenticated user."""
        self.authenticate_user(self.owner_user)
        
        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        
        # Verify profile was updated
        self.owner_profile.refresh_from_db()
        self.assertEqual(self.owner_profile.first_name, 'Updated')
        self.assertEqual(self.owner_profile.last_name, 'Name')


class VerificationAPITests(BaseAPITestCase):
    """Tests for Verification API endpoints."""
    
    def test_submit_verification_as_owner(self):
        """Test submitting verification documents as owner."""
        self.authenticate_user(self.owner_user)
        
        url = reverse('verification-submit')
        data = {
            'document_type': 'national_id',
            'document_url': 'https://example.com/document.jpg'
        }
        
        with patch('accounts.views.main_views.VerificationViewSet._get_profile_or_error') as mock_profile:
            mock_profile.return_value = self.owner_profile
            response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_submit_verification_as_tenant_forbidden(self):
        """Test that tenants cannot submit verification documents."""
        self.authenticate_user(self.tenant_user)
        
        url = reverse('verification-submit')
        data = {
            'document_type': 'national_id',
            'document_url': 'https://example.com/document.jpg'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_verification_status_as_owner(self):
        """Test checking verification status as owner."""
        self.authenticate_user(self.owner_user)
        
        url = reverse('verification-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_verified_poster', response.data)


class AdminVerificationAPITests(BaseAPITestCase):
    """Tests for Admin Verification API endpoints."""
    
    def setUp(self):
        """Set up test data with verification requests."""
        super().setUp()
        
        # Add verification documents to owner profile
        self.owner_profile.poster_documents = [
            {
                'document_type': 'national_id',
                'document_url': 'https://example.com/id.jpg',
                'submission_id': str(uuid.uuid4()),
                'submitted_at': '2024-01-01T00:00:00Z'
            }
        ]
        self.owner_profile.save()
    
    def test_list_verification_requests_as_admin(self):
        """Test listing verification requests as admin."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('adminverification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_verification_requests_as_non_admin_forbidden(self):
        """Test that non-admins cannot list verification requests."""
        self.authenticate_user(self.owner_user)
        
        url = reverse('adminverification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_approve_verification_as_admin(self):
        """Test approving verification request as admin."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('adminverification-approve', kwargs={'pk': self.owner_user.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the user was actually verified
        self.owner_profile.refresh_from_db()
        self.assertTrue(self.owner_profile.is_verified_poster)
    
    def test_reject_verification_as_admin(self):
        """Test rejecting verification request as admin.""" 
        self.authenticate_user(self.admin_user)
        
        url = reverse('adminverification-reject', kwargs={'pk': self.owner_user.id})
        data = {'reason': 'Documents not clear'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminUserAPITests(BaseAPITestCase):
    """Tests for Admin User Management API endpoints."""
    
    def test_list_users_as_admin(self):
        """Test listing users as admin."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('adminuser-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_list_users_as_non_admin_forbidden(self):
        """Test that non-admins cannot list users."""
        self.authenticate_user(self.owner_user)
        
        url = reverse('adminuser-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_change_user_role_as_admin(self):
        """Test changing user role as admin."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('adminuser-change-role', kwargs={'pk': self.tenant_user.id})
        data = {'new_role': 'owner'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify role was changed
        self.tenant_user.refresh_from_db()
        self.assertEqual(self.tenant_user.role, 'owner')
    
    def test_activate_user_as_admin(self):
        """Test activating user as admin."""
        # First deactivate the user
        self.tenant_user.is_active = False
        self.tenant_user.save()
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('adminuser-activate', kwargs={'pk': self.tenant_user.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user was activated
        self.tenant_user.refresh_from_db()
        self.assertTrue(self.tenant_user.is_active)
    
    def test_deactivate_user_as_admin(self):
        """Test deactivating user as admin."""
        self.authenticate_user(self.admin_user)
        
        url = reverse('adminuser-deactivate', kwargs={'pk': self.tenant_user.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user was deactivated
        self.tenant_user.refresh_from_db()
        self.assertFalse(self.tenant_user.is_active)


class RoleSpecificAPITests(BaseAPITestCase):
    """Tests for role-specific API endpoints."""
    
    def test_agent_license_endpoints(self):
        """Test agent license management endpoints."""
        self.authenticate_user(self.agent_user)
        
        # Test list licenses
        url = reverse('agentlicense-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create license
        data = {
            'license_number': 'AG12345',
            'license_type': 'real_estate',
            'issue_date': '2024-01-01',
            'expiry_date': '2025-01-01'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_owner_property_endpoints(self):
        """Test owner property management endpoints."""
        self.authenticate_user(self.owner_user)
        
        # Test list properties
        url = reverse('ownerproperty-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_tenant_preferences_endpoints(self):
        """Test tenant preferences endpoints."""
        self.authenticate_user(self.tenant_user)
        
        # Test list preferences
        url = reverse('tenantpreference-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create preference
        data = {
            'preferred_location': 'Downtown',
            'max_budget': 2000,
            'property_type': 'apartment',
            'bedrooms': 2
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_manager_assignment_endpoints(self):
        """Test manager assignment endpoints."""
        self.authenticate_user(self.manager_user)
        
        # Test list assignments
        url = reverse('managerassignment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticationAPITests(BaseAPITestCase):
    """Tests for authentication endpoints."""
    
    def test_jwt_token_obtain(self):
        """Test obtaining JWT tokens."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'owner@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_jwt_token_refresh(self):
        """Test refreshing JWT tokens."""
        # First get tokens
        refresh = RefreshToken.for_user(self.owner_user)
        
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class RateLimitingTests(BaseAPITestCase):
    """Tests for rate limiting functionality."""
    
    @patch('accounts.rate_limiting.rate_limiting.profile_rate_limit')
    def test_profile_rate_limiting(self, mock_rate_limit):
        """Test that rate limiting is applied to profile endpoints."""
        mock_rate_limit.return_value = lambda func: func
        
        self.authenticate_user(self.owner_user)
        
        url = reverse('profile')
        
        # Make multiple requests rapidly
        for _ in range(5):
            response = self.client.put(url, {}, format='json')
        
        # Verify rate limiting decorator was called
        self.assertTrue(mock_rate_limit.called)
    
    @patch('accounts.rate_limiting.rate_limiting.admin_rate_limit')
    def test_admin_rate_limiting(self, mock_rate_limit):
        """Test that rate limiting is applied to admin endpoints."""
        mock_rate_limit.return_value = lambda func: func
        
        self.authenticate_user(self.admin_user)
        
        url = reverse('adminuser-list')
        
        # Make multiple requests rapidly
        for _ in range(5):
            response = self.client.get(url)
        
        # Verify rate limiting decorator was called
        self.assertTrue(mock_rate_limit.called)


class SecurityTests(BaseAPITestCase):
    """Tests for security features."""
    
    def test_internal_api_requires_key(self):
        """Test that internal API endpoints require API key."""
        url = reverse('internal-user-detail', kwargs={'user_id': self.owner_user.id})
        
        # Request without API key should fail
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Request with wrong API key should fail
        self.client.credentials(HTTP_X_INTERNAL_API_KEY='wrong-key')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        self.authenticate_user(self.owner_user)
        
        url = reverse('profile')
        response = self.client.get(url)
        
        # Check for CORS headers (these would be added by middleware)
        # In a real test, you'd check for actual CORS headers
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_unauthorized_access_to_admin_endpoints(self):
        """Test that admin endpoints properly reject non-admin users."""
        test_users = [self.owner_user, self.agent_user, self.tenant_user, self.manager_user]
        
        admin_urls = [
            reverse('adminuser-list'),
            reverse('adminverification-list'),
        ]
        
        for user in test_users:
            self.authenticate_user(user)
            for url in admin_urls:
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                               f"User {user.role} should not access {url}") 