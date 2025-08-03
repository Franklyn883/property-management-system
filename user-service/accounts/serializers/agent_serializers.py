from rest_framework import serializers
from ..models import UserProfile
from ..validators.validation import ValidationMixin
from datetime import date, timedelta


class AgentLicenseSerializer(serializers.ModelSerializer, ValidationMixin):
    """
    Serializer for agent license management.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'license_id',
            'license_expiration_date',
            'license_documents',
        ]
    
    def validate_license_id(self, value):
        """Validate license ID format."""
        if not value:
            raise serializers.ValidationError("License ID is required for agents")
        
        # Basic validation for license ID format
        if len(value) < 5:
            raise serializers.ValidationError("License ID must be at least 5 characters long")
        
        return value.upper()  # Convert to uppercase
    
    def validate_license_expiration_date(self, value):
        """Validate license expiration date."""
        if value and value <= date.today():
            raise serializers.ValidationError("License expiration date must be in the future")
        return value
    
    def validate_license_documents(self, value):
        """Validate license documents."""
        if not value:
            return []
        
        if not isinstance(value, list):
            raise serializers.ValidationError("License documents must be a list")
        
        for doc in value:
            if not isinstance(doc, dict):
                raise serializers.ValidationError("Each license document must be an object")
            
            required_fields = ['name', 'url', 'type']
            for field in required_fields:
                if field not in doc:
                    raise serializers.ValidationError(f"License document missing required field: {field}")
        
        return value


class AgentAgencySerializer(serializers.ModelSerializer, ValidationMixin):
    """
    Serializer for agent agency information.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'agency_name',
            'clients_managed_count',
        ]
    
    def validate_agency_name(self, value):
        """Validate agency name."""
        if not value:
            raise serializers.ValidationError("Agency name is required for agents")
        
        if len(value) < 3:
            raise serializers.ValidationError("Agency name must be at least 3 characters long")
        
        return value.strip()
    
    def validate_clients_managed_count(self, value):
        """Validate clients managed count."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Clients managed count cannot be negative")
        return value


class AgentStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for agent statistics.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    license_status = serializers.SerializerMethodField()
    days_until_expiration = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user_email',
            'full_name',
            'agency_name',
            'license_id',
            'license_expiration_date',
            'license_status',
            'days_until_expiration',
            'clients_managed_count',
            'is_verified_poster',
            'poster_verification_status',
        ]
    
    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.first_name} {obj.last_name}".strip()
        except:
            return ""
    
    def get_license_status(self, obj):
        """Get license status."""
        if not obj.license_id:
            return "no_license"
        
        if not obj.license_expiration_date:
            return "unknown"
        
        if obj.license_expiration_date <= date.today():
            return "expired"
        elif obj.license_expiration_date <= date.today() + timedelta(days=30):
            return "expiring_soon"
        else:
            return "valid"
    
    def get_days_until_expiration(self, obj):
        """Get days until license expiration."""
        if not obj.license_expiration_date:
            return None
        
        delta = obj.license_expiration_date - date.today()
        return delta.days


class AgentDocumentSerializer(serializers.Serializer, ValidationMixin):
    """
    Serializer for agent document upload.
    """
    
    document_type = serializers.ChoiceField(
        choices=[
            ('license', 'License Document'),
            ('agency_certificate', 'Agency Certificate'),
            ('insurance', 'Insurance Certificate'),
            ('bond', 'Bond Certificate'),
            ('other', 'Other'),
        ]
    )
    document_name = serializers.CharField(max_length=255)
    document_url = serializers.URLField()
    description = serializers.CharField(max_length=500, required=False)
    expiration_date = serializers.DateField(required=False)
    
    def validate_document_url(self, value):
        """Validate document URL."""
        return self.validate_url(value)
    
    def validate_expiration_date(self, value):
        """Validate expiration date."""
        if value and value <= date.today():
            raise serializers.ValidationError("Expiration date must be in the future")
        return value 