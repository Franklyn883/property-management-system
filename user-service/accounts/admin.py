from django.contrib import admin
from .models import CustomUser, UserProfile

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')   

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email')
    search_fields = ('user__email', 'first_name', 'last_name')
    list_filter = ('user__is_staff', 'user__is_superuser', 'user__is_active', 'user__groups')


# Register your models here.
admin.site.register(CustomUser) 
admin.site.register(UserProfile)