from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# =========================
# Custom Admin Actions
# =========================

@admin.action(description='✅ Approve selected doctors')
def approve_doctors(modeladmin, request, queryset):
    queryset.filter(role='doctor').update(is_approved=True)


@admin.action(description='❌ Reject selected doctors')
def reject_doctors(modeladmin, request, queryset):
    queryset.filter(role='doctor').update(is_approved=False)


# =========================
# Custom User Admin
# =========================

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    actions = [approve_doctors, reject_doctors]

    # Table display
    list_display = [
        'email',
        'full_name',
        'role',
        'is_approved',
        'date_joined'
    ]

    # Filters
    list_filter = [
        'role',
        'is_approved',
        'date_joined'
    ]

    # Search
    search_fields = [
        'email',
        'first_name',
        'last_name'
    ]

    # Default ordering
    ordering = ['-date_joined']

    # Allow inline editing (only for doctors ideally)
    list_editable = ['is_approved']

    # Read-only fields
    readonly_fields = ['date_joined', 'last_login']

    # Extra fields in admin form
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Approval Info', {
            'fields': (
                'role',
                'is_approved',
                'specialization',
                'phone',
                'date_of_birth'
            )
        }),
    )

    # =========================
    # Custom Methods
    # =========================

    def full_name(self, obj):
        return obj.get_full_name() or obj.email
    full_name.short_description = 'Name'

    # Optional: prevent editing approval for non-doctors
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.role != 'doctor':
            return self.readonly_fields + ('is_approved',)
        return self.readonly_fields