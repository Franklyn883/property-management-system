from django.contrib import admin
from .models import CustomUser, UserProfile


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "get_full_name",
        "role",
        "is_verified",
        "is_active",
        "date_joined",
    )
    search_fields = ("email", "phone_number")
    list_filter = (
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "date_joined",
    )
    readonly_fields = ("id", "date_joined", "updated_at", "last_login")
    ordering = ("-date_joined",)

    fieldsets = (
        ("Basic Information", {"fields": ("email", "phone_number", "role")}),
        (
            "Status",
            {
                "fields": (
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("id", "date_joined", "updated_at", "last_login"),
                "classes": ("collapse",),
            },
        ),
        (
            "Permissions",
            {
                "fields": ("groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_full_name(self, obj):
        if hasattr(obj, "profile") and obj.profile:
            return obj.profile.get_full_name
        return "No Profile"

    get_full_name.short_description = "Full Name"


class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "get_email",
        "get_full_name",
        "user_role",
        "is_verified_poster",
        "poster_verification_status",
        "created_at",
    )
    search_fields = ("user__email", "first_name", "last_name", "user__role")
    list_filter = (
        "user__role",
        "is_verified_poster",
        "poster_verification_status",
        "user__is_verified",
        "user__is_active",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "User Information",
            {
                "fields": (
                    "user",
                    "first_name",
                    "last_name",
                    "avatar_url",
                    "bio",
                    "gender",
                    "date_of_birth",
                )
            },
        ),
        (
            "Contact Information",
            {"fields": ("address", "city", "state", "country", "zip_code")},
        ),
        (
            "Preferences",
            {
                "fields": (
                    "notification_preferences",
                    "saved_searches",
                    "wishlist",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Verification Status",
            {
                "fields": (
                    "is_verified_poster",
                    "poster_verification_status",
                    "verified_at",
                    "poster_documents",
                )
            },
        ),
        (
            "Agent Information",
            {
                "fields": (
                    "agency_name",
                    "license_id",
                    "license_expiration_date",
                    "license_documents",
                    "clients_managed_count",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Owner Information",
            {
                "fields": ("ownership_documents", "properties_owned_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Tenant Information",
            {
                "fields": (
                    "tenant_documents",
                    "properties_rented_count",
                    "rental_history_rating",
                    "preferred_locations",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Manager Information",
            {
                "fields": (
                    "properties_managed_count",
                    "assigned_properties",
                    "maintenance_requests_handled_count",
                    "assigned_maintenance_requests",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"
    get_email.admin_order_field = "user__email"

    def get_full_name(self, obj):
        return obj.get_full_name

    get_full_name.short_description = "Full Name"
    get_full_name.admin_order_field = "first_name"

    def user_role(self, obj):
        return obj.user.get_role_display()

    user_role.short_description = "Role"
    user_role.admin_order_field = "user__role"


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
