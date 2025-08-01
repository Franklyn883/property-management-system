from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync existing users is_verified field based on their allauth email verification status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('Starting email verification sync...')
        )
        
        # Get all users
        users = User.objects.all()
        total_users = users.count()
        
        # Get verified email addresses from allauth
        verified_emails = EmailAddress.objects.filter(verified=True)
        verified_user_ids = set(verified_emails.values_list('user_id', flat=True))
        
        # Find users who should be verified but aren't
        users_to_verify = []
        users_already_verified = []
        users_unverified = []
        
        for user in users:
            if user.id in verified_user_ids:
                if user.is_verified:
                    users_already_verified.append(user)
                else:
                    users_to_verify.append(user)
            else:
                users_unverified.append(user)
        
        # Display summary
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  Total users: {total_users}')
        self.stdout.write(f'  Users to verify: {len(users_to_verify)}')
        self.stdout.write(f'  Users already verified: {len(users_already_verified)}')
        self.stdout.write(f'  Users unverified: {len(users_unverified)}')
        
        if verbose:
            if users_to_verify:
                self.stdout.write(f'\nUsers to be verified:')
                for user in users_to_verify:
                    self.stdout.write(f'  - {user.email} (ID: {user.id})')
            
            if users_already_verified:
                self.stdout.write(f'\nUsers already verified:')
                for user in users_already_verified:
                    self.stdout.write(f'  - {user.email} (ID: {user.id})')
        
        # Update users if not dry run
        if users_to_verify and not dry_run:
            self.stdout.write(f'\nUpdating {len(users_to_verify)} users...')
            
            with transaction.atomic():
                for user in users_to_verify:
                    user.is_verified = True
                    user.save(update_fields=['is_verified'])
                    self.stdout.write(f'  ✓ Verified: {user.email}')
            
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully updated {len(users_to_verify)} users!')
            )
        
        elif users_to_verify and dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nDRY RUN: Would update {len(users_to_verify)} users')
            )
            for user in users_to_verify:
                self.stdout.write(f'  Would verify: {user.email}')
        
        elif not users_to_verify:
            self.stdout.write(
                self.style.SUCCESS(f'\nNo users need to be updated. All verified users are already synced!')
            )
        
        self.stdout.write('\nSync completed!') 