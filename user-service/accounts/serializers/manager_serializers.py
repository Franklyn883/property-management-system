from rest_framework import serializers
from .models import UserProfile
from .validation import ValidationMixin
from datetime import date


class ManagerAssignmentSerializer(serializers.ModelSerializer, ValidationMixin):
    """
    Serializer for manager property assignments.
    """

    class Meta:
        model = UserProfile
        fields = [
            "assigned_properties",
            "management_contracts",
        ]

    def validate_assigned_properties(self, value):
        """Validate assigned properties."""
        if not value:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Assigned properties must be a list"
            )

        for prop in value:
            if not isinstance(prop, dict):
                raise serializers.ValidationError(
                    "Each assigned property must be an object"
                )

            required_fields = [
                "property_id",
                "property_address",
                "assignment_date",
            ]
            for field in required_fields:
                if field not in prop:
                    raise serializers.ValidationError(
                        f"Assigned property missing required field: {field}"
                    )

        return value

    def validate_management_contracts(self, value):
        """Validate management contracts."""
        if not value:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Management contracts must be a list"
            )

        for contract in value:
            if not isinstance(contract, dict):
                raise serializers.ValidationError(
                    "Each management contract must be an object"
                )

            required_fields = [
                "contract_id",
                "property_id",
                "start_date",
                "commission_rate",
            ]
            for field in required_fields:
                if field not in contract:
                    raise serializers.ValidationError(
                        f"Management contract missing required field: {field}"
                    )

        return value


class ManagerMaintenanceSerializer(serializers.ModelSerializer):
    """
    Serializer for manager maintenance requests.
    """

    user_email = serializers.CharField(source="user.email", read_only=True)
    full_name = serializers.SerializerMethodField()
    active_requests_count = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "user_email",
            "full_name",
            "maintenance_requests",
            "active_requests_count",
        ]

    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.first_name} {obj.last_name}".strip()
        except:
            return ""

    def get_active_requests_count(self, obj):
        """Get count of active maintenance requests."""
        requests = obj.maintenance_requests or []
        active_count = 0
        for request in requests:
            if request.get("status") in ["pending", "in_progress"]:
                active_count += 1
        return active_count


class ManagerDashboardSerializer(serializers.ModelSerializer):
    """
    Serializer for manager dashboard analytics.
    """

    user_email = serializers.CharField(source="user.email", read_only=True)
    full_name = serializers.SerializerMethodField()
    total_properties = serializers.SerializerMethodField()
    total_contracts = serializers.SerializerMethodField()
    total_requests = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "user_email",
            "full_name",
            "assigned_properties",
            "management_contracts",
            "maintenance_requests",
            "total_properties",
            "total_contracts",
            "total_requests",
        ]

    def get_full_name(self, obj):
        """Get the full name from the user's profile."""
        try:
            return f"{obj.first_name} {obj.last_name}".strip()
        except:
            return ""

    def get_total_properties(self, obj):
        """Get total number of assigned properties."""
        return len(obj.assigned_properties or [])

    def get_total_contracts(self, obj):
        """Get total number of management contracts."""
        return len(obj.management_contracts or [])

    def get_total_requests(self, obj):
        """Get total number of maintenance requests."""
        return len(obj.maintenance_requests or [])


class ManagerAssignmentEntrySerializer(serializers.Serializer, ValidationMixin):
    """
    Serializer for adding property assignments.
    """

    property_id = serializers.CharField(max_length=100)
    property_address = serializers.CharField(max_length=255)
    assignment_date = serializers.DateField()
    owner_name = serializers.CharField(max_length=100, required=False)
    owner_contact = serializers.CharField(max_length=100, required=False)
    management_fee = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False
    )
    notes = serializers.CharField(max_length=500, required=False)

    def validate_assignment_date(self, value):
        """Validate assignment date."""
        if value > date.today():
            raise serializers.ValidationError(
                "Assignment date cannot be in the future"
            )
        return value

    def validate_management_fee(self, value):
        """Validate management fee."""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError(
                "Management fee must be between 0 and 100"
            )
        return value


class ManagerMaintenanceEntrySerializer(
    serializers.Serializer, ValidationMixin
):
    """
    Serializer for adding maintenance requests.
    """

    property_id = serializers.CharField(max_length=100)
    property_address = serializers.CharField(max_length=255)
    issue_type = serializers.ChoiceField(
        choices=[
            ("repair", "Repair"),
            ("maintenance", "Maintenance"),
            ("emergency", "Emergency"),
            ("inspection", "Inspection"),
            ("cleaning", "Cleaning"),
            ("other", "Other"),
        ]
    )
    priority = serializers.ChoiceField(
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("urgent", "Urgent"),
        ]
    )
    description = serializers.CharField(max_length=1000)
    reported_date = serializers.DateField()
    estimated_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    contractor_name = serializers.CharField(max_length=100, required=False)
    contractor_contact = serializers.CharField(max_length=100, required=False)

    def validate_reported_date(self, value):
        """Validate reported date."""
        if value > date.today():
            raise serializers.ValidationError(
                "Reported date cannot be in the future"
            )
        return value

    def validate_estimated_cost(self, value):
        """Validate estimated cost."""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Estimated cost cannot be negative"
            )
        return value


class ManagerContractEntrySerializer(serializers.Serializer, ValidationMixin):
    """
    Serializer for adding management contracts.
    """

    contract_id = serializers.CharField(max_length=100)
    property_id = serializers.CharField(max_length=100)
    property_address = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    owner_name = serializers.CharField(max_length=100)
    owner_contact = serializers.CharField(max_length=100, required=False)
    contract_terms = serializers.CharField(max_length=1000, required=False)

    def validate_start_date(self, value):
        """Validate start date."""
        if value > date.today():
            raise serializers.ValidationError(
                "Start date cannot be in the future"
            )
        return value

    def validate_end_date(self, value):
        """Validate end date."""
        if value and value > date.today():
            raise serializers.ValidationError(
                "End date cannot be in the future"
            )
        return value

    def validate_commission_rate(self, value):
        """Validate commission rate."""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Commission rate must be between 0 and 100"
            )
        return value

    def validate(self, data):
        """Validate date range."""
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date cannot be before start date"
            )

        return data
