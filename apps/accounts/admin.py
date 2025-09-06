from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active_member', 'is_staff')
    list_filter = ('role', 'is_active_member', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        (_('Church Information'), {
            'fields': ('role', 'phone', 'bio', 'avatar', 'date_of_birth', 'address', 
                      'emergency_contact', 'membership_date', 'is_active_member', 
                      'ministry_affiliations', 'email_verified')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Church Information'), {
            'fields': ('email', 'role', 'phone', 'membership_date')
        }),
    )
