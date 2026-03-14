from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.action(description='✅ Approve selected doctors')
def approve_doctors(modeladmin, request, queryset):
    queryset.filter(role='doctor').update(is_approved=True)


@admin.action(description='❌ Reject selected doctors')
def reject_doctors(modeladmin, request, queryset):
    queryset.filter(role='doctor').update(is_approved=False)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    actions = [approve_doctors, reject_doctors]

    list_display  = ['email', 'full_name', 'role', 'is_approved', 'date_joined']
    list_filter   = ['role', 'is_approved']
    search_fields = ['email', 'first_name', 'last_name']
    ordering      = ['-date_joined']

    list_editable = ['is_approved']  # ← approve directly from list

    fieldsets = UserAdmin.fieldsets + (
        ('Role & Approval', {
            'fields': ('role', 'is_approved', 'specialization', 'phone', 'date_of_birth')
        }),
    )

    def full_name(self, obj):
        return obj.get_full_name() or obj.username
    full_name.short_description = 'Name'