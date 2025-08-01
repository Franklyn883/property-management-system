from django.test import TestCase
from django.contrib.auth import get_user_model
from allauth.account.signals import email_confirmed
from django.dispatch import Signal
from unittest.mock import Mock
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
from allauth.account.models import EmailAddress

User = get_user_model()


class EmailVerificationSignalTest(TestCase):
    """Test that email verification signal properly updates user.is_verified"""
    
    def test_email_confirmation_sets_is_verified(self):
        """Test that when email is confirmed, user.is_verified is set to True"""
        # Create a user with unverified email
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Verify user starts as unverified
        self.assertFalse(user.is_verified)
        
        # Create a mock email address object
        mock_email_address = Mock()
        mock_email_address.user = user
        
        # Trigger the email_confirmed signal
        email_confirmed.send(
            sender=self.__class__,
            email_address=mock_email_address
        )
        
        # Refresh user from database
        user.refresh_from_db()
        
        # Verify that is_verified is now True
        self.assertTrue(user.is_verified)


class SyncEmailVerificationCommandTest(TestCase):
    """Test the sync_email_verification management command"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            is_verified=False
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='testpass123',
            is_verified=False
        )
        self.user3 = User.objects.create_user(
            email='user3@example.com',
            password='testpass123',
            is_verified=True
        )
        
        # Create email addresses in allauth
        self.email1 = EmailAddress.objects.create(
            user=self.user1,
            email='user1@example.com',
            verified=True,
            primary=True
        )
        self.email2 = EmailAddress.objects.create(
            user=self.user2,
            email='user2@example.com',
            verified=False,
            primary=True
        )
        self.email3 = EmailAddress.objects.create(
            user=self.user3,
            email='user3@example.com',
            verified=True,
            primary=True
        )
    
    def test_sync_command_dry_run(self):
        """Test the sync command in dry-run mode"""
        out = StringIO()
        
        # Run the command in dry-run mode
        call_command('sync_email_verification', '--dry-run', stdout=out)
        
        output = out.getvalue()
        
        # Check that the command ran without errors
        self.assertIn('Starting email verification sync...', output)
        self.assertIn('Users to verify: 1', output)  # user1 should be verified
        self.assertIn('DRY RUN: Would update 1 users', output)
        self.assertIn('Would verify: user1@example.com', output)
        
        # Verify no changes were made (dry run)
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_verified)
    
    def test_sync_command_actual_run(self):
        """Test the sync command actually updates users"""
        out = StringIO()
        
        # Run the command
        call_command('sync_email_verification', stdout=out)
        
        output = out.getvalue()
        
        # Check that the command ran without errors
        self.assertIn('Starting email verification sync...', output)
        self.assertIn('Successfully updated 1 users!', output)
        self.assertIn('✓ Verified: user1@example.com', output)
        
        # Verify changes were made
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_verified)
        
        # Verify other users weren't changed
        self.user2.refresh_from_db()
        self.user3.refresh_from_db()
        self.assertFalse(self.user2.is_verified)  # Not verified in allauth
        self.assertTrue(self.user3.is_verified)   # Already verified
    
    def test_sync_command_verbose(self):
        """Test the sync command with verbose output"""
        out = StringIO()
        
        # Run the command with verbose flag
        call_command('sync_email_verification', '--verbose', '--dry-run', stdout=out)
        
        output = out.getvalue()
        
        # Check verbose output
        self.assertIn('Users to be verified:', output)
        self.assertIn('- user1@example.com (ID:', output)
        self.assertIn('Users already verified:', output)
        self.assertIn('- user3@example.com (ID:', output)
