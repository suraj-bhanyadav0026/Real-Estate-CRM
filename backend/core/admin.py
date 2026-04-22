from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active_agent', 'date_joined')
    list_filter = ('role', 'is_active_agent')
    search_fields = ('email', 'first_name', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Agent Info', {'fields': ('phone', 'profile_photo', 'specialization', 'role', 'is_active_agent')}),
    )

from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'status', 'score', 'assigned_to', 'created_at')
    list_filter = ('status', 'source', 'assigned_to')
    search_fields = ('name', 'phone', 'email')
    readonly_fields = ('score', 'created_at', 'updated_at')
    list_editable = ('status',)
    raw_id_fields = ('assigned_to',)

