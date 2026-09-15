from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "department")
    search_fields = ("user__username", "employee_code", "organization__commercial_name", "department__name")
    list_filter = ("organization", "department")
    list_select_related = ("user", "organization", "department")
