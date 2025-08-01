# Email Verification Integration with Django Allauth

This document explains how email verification is integrated with Django allauth to automatically update the `is_verified` field in the custom user model.

## How It Works

### Signal Handler
The email verification is handled by a Django signal in `accounts/signals.py`:

```python
@receiver(email_confirmed)
def handle_email_confirmation(sender, email_address, **kwargs):
    """
    Sets the user's is_verified field to True when their email is confirmed by allauth.
    """
    user = email_address.user
    if user and not user.is_verified:
        user.is_verified = True
        user.save(update_fields=['is_verified'])
```

### Allauth Configuration
The allauth settings in `users/settings.py` are configured for mandatory email verification:

```python
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
```

## Flow

1. User registers with email address
2. Allauth sends verification email
3. User clicks verification link
4. Allauth confirms the email
5. The `email_confirmed` signal is triggered
6. Our signal handler sets `user.is_verified = True`
7. User can now access features that require verification

## Handling Existing Users

For users who already verified their email through allauth before this integration was added, you can sync their verification status using the management command:

### Running the Sync Command

**In Docker environment:**
```bash
# Dry run to see what would be updated
docker-compose exec user-service python manage.py sync_email_verification --dry-run --verbose

# Actually update the users
docker-compose exec user-service python manage.py sync_email_verification

# With verbose output
docker-compose exec user-service python manage.py sync_email_verification --verbose
```

**Local development:**
```bash
# Dry run to see what would be updated
python manage.py sync_email_verification --dry-run --verbose

# Actually update the users
python manage.py sync_email_verification

# With verbose output
python manage.py sync_email_verification --verbose
```

### What the Sync Command Does

1. **Analyzes existing users**: Checks all users in your database
2. **Checks allauth verification status**: Looks at the `EmailAddress` model to see which emails are verified
3. **Identifies mismatches**: Finds users whose allauth email is verified but `is_verified` field is `False`
4. **Updates users**: Sets `is_verified = True` for users who should be verified
5. **Provides detailed output**: Shows summary and individual user updates

### Command Options

- `--dry-run`: Shows what would be updated without making changes
- `--verbose`: Shows detailed information about each user

### Example Output

```
Starting email verification sync...

Summary:
  Total users: 150
  Users to verify: 25
  Users already verified: 100
  Users unverified: 25

Users to be verified:
  - user1@example.com (ID: 123)
  - user2@example.com (ID: 124)
  ...

Updating 25 users...
  ✓ Verified: user1@example.com
  ✓ Verified: user2@example.com
  ...

Successfully updated 25 users!
```

## Testing

Run the test to verify the integration works:

```bash
# In Docker
docker-compose exec user-service python manage.py test accounts.tests.EmailVerificationSignalTest

# Local development
python manage.py test accounts.tests.EmailVerificationSignalTest
```

## Benefits

- **Automatic**: No manual intervention required for new users
- **Backward Compatible**: Sync command handles existing users
- **Consistent**: Uses allauth's built-in verification system
- **Secure**: Leverages allauth's security features
- **Testable**: Includes unit tests for verification
- **Maintainable**: Simple signal handler, easy to understand and modify
- **Safe**: Dry-run option lets you preview changes before applying them 