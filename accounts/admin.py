from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'get_display_name', 'email', 'role_badge',
        'gender', 'is_staff', 'is_active', 'date_joined'
    )
    list_filter = ('role', 'gender', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'full_name_ar', 'phone')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('الدور والنوع', {
            'fields': ('role',)
        }),
        ('معلومات الملف الشخصي', {
            'fields': (
                'full_name_ar', 'gender', 'phone', 'birth_date',
                'bio', 'avatar'
            )
        }),
        ('التفضيلات', {
            'fields': ('receive_notifications',),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('معلومات إضافية', {
            'fields': ('email', 'role', 'full_name_ar', 'gender'),
        }),
    )

    def role_badge(self, obj):
        colors = {
            'blind': '#9333ea',
            'librarian': '#1E4ED8',
        }
        color = colors.get(obj.role, '#64748b')
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; '
            'border-radius:3px; font-size:11px;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'نوع الحساب'
