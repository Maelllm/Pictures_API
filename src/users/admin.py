from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = "__all__"


class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm
    model = CustomUser
    list_display = (
        "email",
        "user_type",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "user_type",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Custom fields", {"fields": ("user_type",)}),  # Add the custom field to this tuple
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "user_type"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(get_user_model(), CustomUserAdmin)
