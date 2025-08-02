import re
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class PasswordStrengthValidator:
    """
    Validator for password strength requirements.
    """
    
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True, 
                 require_digits=True, require_special=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
    
    def validate(self, password):
        """
        Validate password strength.
        """
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return password


class EmailDomainValidator:
    """
    Validator for email domain validation.
    """
    
    def __init__(self, allowed_domains=None, blocked_domains=None):
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
    
    def validate(self, email):
        """
        Validate email domain.
        """
        try:
            # Validate email format
            validated_email = validate_email(email)
            domain = validated_email.domain
            
            # Check blocked domains
            if domain in self.blocked_domains:
                raise serializers.ValidationError(f"Email domain '{domain}' is not allowed")
            
            # Check allowed domains (if specified)
            if self.allowed_domains and domain not in self.allowed_domains:
                raise serializers.ValidationError(f"Email domain '{domain}' is not in allowed domains")
            
            return email
            
        except EmailNotValidError as e:
            raise serializers.ValidationError(f"Invalid email format: {str(e)}")


class PhoneNumberValidator:
    """
    Validator for phone number validation.
    """
    
    def __init__(self, default_region='US'):
        self.default_region = default_region
    
    def validate(self, phone_number):
        """
        Validate phone number format and existence.
        """
        if not phone_number:
            return phone_number
        
        try:
            # Parse phone number
            parsed_number = phonenumbers.parse(phone_number, self.default_region)
            
            # Check if number is valid
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError("Invalid phone number format")
            
            # Check if number is possible
            if not phonenumbers.is_possible_number(parsed_number):
                raise serializers.ValidationError("Phone number is not possible")
            
            # Format number in international format
            formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            
            return formatted_number
            
        except phonenumbers.NumberParseException as e:
            raise serializers.ValidationError(f"Invalid phone number: {str(e)}")


class NameValidator:
    """
    Validator for name fields (first name, last name).
    """
    
    def __init__(self, min_length=2, max_length=50):
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, name):
        """
        Validate name format and length.
        """
        if not name:
            raise serializers.ValidationError("Name is required")
        
        # Remove extra whitespace
        name = name.strip()
        
        if len(name) < self.min_length:
            raise serializers.ValidationError(f"Name must be at least {self.min_length} characters long")
        
        if len(name) > self.max_length:
            raise serializers.ValidationError(f"Name must be no more than {self.max_length} characters long")
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-Z\s\'-]+$', name):
            raise serializers.ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes")
        
        # Check for consecutive special characters
        if re.search(r'[\s\'-]{2,}', name):
            raise serializers.ValidationError("Name cannot contain consecutive special characters")
        
        return name


class AgeValidator:
    """
    Validator for age/date of birth validation.
    """
    
    def __init__(self, min_age=13, max_age=120):
        self.min_age = min_age
        self.max_age = max_age
    
    def validate(self, date_of_birth):
        """
        Validate date of birth and age requirements.
        """
        if not date_of_birth:
            return date_of_birth
        
        from datetime import date
        today = date.today()
        
        # Calculate age
        age = today.year - date_of_birth.year - (
            (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
        )
        
        if age < self.min_age:
            raise serializers.ValidationError(f"User must be at least {self.min_age} years old")
        
        if age > self.max_age:
            raise serializers.ValidationError(f"Age cannot exceed {self.max_age} years")
        
        return date_of_birth


class URLValidator:
    """
    Validator for URL fields.
    """
    
    def __init__(self, allowed_schemes=None):
        self.allowed_schemes = allowed_schemes or ['http', 'https']
    
    def validate(self, url):
        """
        Validate URL format and security.
        """
        if not url:
            return url
        
        # Basic URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            raise serializers.ValidationError("Invalid URL format")
        
        # Check for allowed schemes
        scheme = url.split('://')[0].lower()
        if scheme not in self.allowed_schemes:
            raise serializers.ValidationError(f"URL scheme '{scheme}' is not allowed")
        
        return url


class ValidationMixin:
    """
    Mixin for common validation methods.
    """
    
    def validate_password_strength(self, password):
        """
        Validate password strength using PasswordStrengthValidator.
        """
        validator = PasswordStrengthValidator()
        return validator.validate(password)
    
    def validate_email_domain(self, email):
        """
        Validate email domain using EmailDomainValidator.
        """
        validator = EmailDomainValidator()
        return validator.validate(email)
    
    def validate_phone_number(self, phone_number):
        """
        Validate phone number using PhoneNumberValidator.
        """
        validator = PhoneNumberValidator()
        return validator.validate(phone_number)
    
    def validate_name(self, name):
        """
        Validate name using NameValidator.
        """
        validator = NameValidator()
        return validator.validate(name)
    
    def validate_age(self, date_of_birth):
        """
        Validate age using AgeValidator.
        """
        validator = AgeValidator()
        return validator.validate(date_of_birth)
    
    def validate_url(self, url):
        """
        Validate URL using URLValidator.
        """
        validator = URLValidator()
        return validator.validate(url) 