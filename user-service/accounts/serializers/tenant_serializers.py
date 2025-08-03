from rest_framework import serializers
from ..models import UserProfile
from ..validators.validation import ValidationMixin
from datetime import date, timedelta


class TenantPreferenceSerializer(serializers.ModelSerializer, ValidationMixin):
    """
    Serializer for tenant rental preferences.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'rental_preferences',
            'preferred_locations',
            'budget_range',
            'property_type_preferences',
        ]
    
    def validate_rental_preferences(self, value):
        """Validate rental preferences."""
        if not value:
            return {}
        
        if not isinstance(value, dict):
            raise serializers.ValidationError("Rental preferences must be an object")
        
        allowed_keys = [
            'max_rent', 'min_bedrooms', 'max_bedrooms', 'min_bathrooms', 
            'max_bathrooms', 'parking_required', 'pet_friendly', 
            'furnished', 'utilities_included', 'lease_duration'
        ]
        
        for key in value.keys():
            if key not in allowed_keys:
                raise serializers.ValidationError(f"Invalid preference key: {key}")
        
        return value
    
    def validate_preferred_locations(self, value):
        """Validate preferred locations."""
        if not value:
            return []
        
        if not isinstance(value, list):
            raise serializers.ValidationError("Preferred locations must be a list")
        
        for location in value:
            if not isinstance(location, str) or len(location.strip()) < 3:
                raise serializers.ValidationError("Each location must be a string with at least 3 characters")
        
        return [loc.strip() for loc in value]
    
    def validate_budget_range(self, value):
        """Validate budget range."""
        if not value:
            return {}
        
        if not isinstance(value, dict):
            raise serializers.ValidationError("Budget range must be an object")
        
        required_keys = ['min', 'max']
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(f"Budget range missing required key: {key}")
        
        if value['min'] < 0 or value['max'] < 0:
            raise serializers.ValidationError("Budget values cannot be negative")
        
        if value['min'] > value['max']:
            raise serializers.ValidationError("Minimum budget cannot be greater than maximum budget")
        
        return value
    
    def validate_property_type_preferences(self, value):
        """Validate property type preferences."""
        if not value:
            return []
        
        if not isinstance(value, list):
            raise serializers.ValidationError("Property type preferences must be a list")
        
        allowed_types = [
            'apartment', 'house', 'condo', 'townhouse', 'studio', 
            'loft', 'duplex', 'penthouse', 'villa'
        ]
        
        for prop_type in value:
            if prop_type not in allowed_types:
                raise serializers.ValidationError(f"Invalid property type: {prop_type}")
        
        return value


class TenantHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for tenant rental history.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    rental_history_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user_email',
            'full_name',
            'rental_history',
            'rental_history_count',
        ]
    
    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.first_name} {obj.last_name}".strip()
        except:
            return ""
    
    def get_rental_history_count(self, obj):
        """Get count of rental history entries."""
        return len(obj.rental_history or [])


class TenantRatingSerializer(serializers.ModelSerializer):
    """
    Serializer for tenant rating system.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user_email',
            'full_name',
            'tenant_ratings',
            'average_rating',
            'total_reviews',
        ]
    
    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.first_name} {obj.last_name}".strip()
        except:
            return ""
    
    def get_average_rating(self, obj):
        """Calculate average rating."""
        ratings = obj.tenant_ratings or []
        if not ratings:
            return 0.0
        
        total_rating = sum(rating.get('rating', 0) for rating in ratings)
        return round(total_rating / len(ratings), 1)
    
    def get_total_reviews(self, obj):
        """Get total number of reviews."""
        return len(obj.tenant_ratings or [])


class TenantHistoryEntrySerializer(serializers.Serializer, ValidationMixin):
    """
    Serializer for adding rental history entries.
    """
    
    property_address = serializers.CharField(max_length=255)
    landlord_name = serializers.CharField(max_length=100, required=False)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)
    monthly_rent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason_for_leaving = serializers.CharField(max_length=500, required=False)
    contact_reference = serializers.CharField(max_length=100, required=False)
    reference_phone = serializers.CharField(max_length=20, required=False)
    reference_email = serializers.EmailField(required=False)
    
    def validate_start_date(self, value):
        """Validate start date."""
        if value > date.today():
            raise serializers.ValidationError("Start date cannot be in the future")
        return value
    
    def validate_end_date(self, value):
        """Validate end date."""
        if value and value > date.today():
            raise serializers.ValidationError("End date cannot be in the future")
        return value
    
    def validate(self, data):
        """Validate date range."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError("End date cannot be before start date")
        
        return data


class TenantRatingEntrySerializer(serializers.Serializer, ValidationMixin):
    """
    Serializer for adding tenant ratings.
    """
    
    rating = serializers.IntegerField(min_value=1, max_value=5)
    review_text = serializers.CharField(max_length=1000, required=False)
    landlord_name = serializers.CharField(max_length=100, required=False)
    property_address = serializers.CharField(max_length=255, required=False)
    lease_period = serializers.CharField(max_length=100, required=False)
    categories = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('punctual_payment', 'Punctual Payment'),
            ('property_care', 'Property Care'),
            ('communication', 'Communication'),
            ('cleanliness', 'Cleanliness'),
            ('noise_level', 'Noise Level'),
            ('cooperation', 'Cooperation'),
        ]),
        required=False
    )
    
    def validate_rating(self, value):
        """Validate rating value."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate_review_text(self, value):
        """Validate review text."""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Review text must be at least 10 characters long")
        return value 