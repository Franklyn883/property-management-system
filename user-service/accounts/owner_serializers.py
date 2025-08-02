from rest_framework import serializers
from .models import UserProfile
from .validation import ValidationMixin
from datetime import date


class OwnerPropertySerializer(serializers.ModelSerializer, ValidationMixin):
    """
    Serializer for owner property information.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'properties_owned_count',
            'ownership_documents',
        ]
    
    def validate_properties_owned_count(self, value):
        """Validate properties owned count."""
        if value is not None and value < 0:
            raise serializers.ValidationError("Properties owned count cannot be negative")
        return value
    
    def validate_ownership_documents(self, value):
        """Validate ownership documents."""
        if not value:
            return []
        
        if not isinstance(value, list):
            raise serializers.ValidationError("Ownership documents must be a list")
        
        for doc in value:
            if not isinstance(doc, dict):
                raise serializers.ValidationError("Each ownership document must be an object")
            
            required_fields = ['name', 'url', 'type']
            for field in required_fields:
                if field not in doc:
                    raise serializers.ValidationError(f"Ownership document missing required field: {field}")
        
        return value


class OwnerVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for owner verification information.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    verification_status = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user_email',
            'full_name',
            'is_verified_poster',
            'poster_verification_status',
            'verified_at',
            'properties_owned_count',
            'ownership_documents',
            'verification_status',
        ]
    
    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.first_name} {obj.last_name}".strip()
        except:
            return ""
    
    def get_verification_status(self, obj):
        """Get verification status."""
        if obj.is_verified_poster:
            return "verified"
        elif obj.poster_verification_status == "pending":
            return "pending"
        elif obj.poster_verification_status == "rejected":
            return "rejected"
        else:
            return "not_submitted"


class OwnerAnalyticsSerializer(serializers.ModelSerializer):
    """
    Serializer for owner analytics.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    days_since_verification = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user_email',
            'full_name',
            'properties_owned_count',
            'is_verified_poster',
            'poster_verification_status',
            'verified_at',
            'ownership_documents',
            'days_since_verification',
            'documents_count',
        ]
    
    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.first_name} {obj.last_name}".strip()
        except:
            return ""
    
    def get_days_since_verification(self, obj):
        """Get days since verification."""
        if obj.verified_at:
            delta = date.today() - obj.verified_at.date()
            return delta.days
        return None
    
    def get_documents_count(self, obj):
        """Get count of ownership documents."""
        return len(obj.ownership_documents or [])


class OwnerDocumentSerializer(serializers.Serializer, ValidationMixin):
    """
    Serializer for owner document upload.
    """
    
    document_type = serializers.ChoiceField(
        choices=[
            ('deed', 'Property Deed'),
            ('title', 'Property Title'),
            ('tax_assessment', 'Tax Assessment'),
            ('insurance', 'Property Insurance'),
            ('survey', 'Property Survey'),
            ('other', 'Other'),
        ]
    )
    document_name = serializers.CharField(max_length=255)
    document_url = serializers.URLField()
    description = serializers.CharField(max_length=500, required=False)
    property_address = serializers.CharField(max_length=255, required=False)
    
    def validate_document_url(self, value):
        """Validate document URL."""
        return self.validate_url(value)
    
    def validate_property_address(self, value):
        """Validate property address."""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Property address must be at least 10 characters long")
        return value.strip() if value else value 