from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    """
    Admin panel untuk Custom User Model.
    Extends Django bawaan UserAdmin agar form password tetap berfungsi.
    """

    list_display = (
        "username",
        "get_nama_lengkap",
        "email",
        "role_badge",
        "is_active",
        "date_joined",
    )
    list_filter = ("role", "is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    list_per_page = 25

    # Tambah field 'role' ke fieldsets bawaan UserAdmin
    fieldsets = UserAdmin.fieldsets + (
        (
            "Informasi MEDESKA",
            {
                "fields": ("role",),
            },
        ),
    )

    # Tambah field 'role' ke form tambah user baru
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Informasi MEDESKA",
            {
                "classes": ("wide",),
                "fields": ("email", "role"),
            },
        ),
    )

    @admin.display(description="Nama Lengkap")
    def get_nama_lengkap(self, obj):
        return obj.get_full_name() or "-"

    @admin.display(description="Role")
    def role_badge(self, obj):
        colors = {
            User.Role.ADMIN: ("#0C447C", "#E6F1FB"),
            User.Role.SISWA: ("#3B6D11", "#EAF3DE"),
        }
        fg, bg = colors.get(obj.role, ("#444441", "#F1EFE8"))
        return format_html(
            '<span style="'
            "background:{bg};color:{fg};padding:2px 10px;"
            'border-radius:10px;font-size:12px;font-weight:500">{label}</span>',
            bg=bg,
            fg=fg,
            label=obj.get_role_display(),
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()