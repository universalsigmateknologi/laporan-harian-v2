from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Pembimbing, Siswa


class SiswaInline(admin.TabularInline):
    """
    Tampilkan daftar siswa langsung di dalam halaman detail Pembimbing.
    Hanya read-only — edit siswa dilakukan dari halaman Siswa.
    """

    model = Siswa
    fields = ("nama_lengkap", "nis", "jurusan", "angkatan", "is_active")
    readonly_fields = ("nama_lengkap", "nis", "jurusan", "angkatan", "is_active")
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = "Siswa Binaan"
    verbose_name_plural = "Daftar Siswa Binaan"


@admin.register(Pembimbing)
class PembimbingAdmin(admin.ModelAdmin):
    list_display = (
        "nama_lengkap",
        "nip",
        "jabatan",
        "no_hp",
        "get_email",
        "jumlah_siswa",
        "status_badge",
    )

    @admin.display(description="Jumlah Siswa")
    def jumlah_siswa(self, obj):
        count = obj.siswa_set.count()
        return format_html(
            '<span style="color:{};font-weight:500">{}</span>',
            "#3B6D11" if count > 0 else "#888780",
            count,
        )
    list_filter = ("is_active",)
    search_fields = ("nama_lengkap", "nip", "jabatan")
    ordering = ("nama_lengkap",)
    list_per_page = 25
    autocomplete_fields = ["user"]
    inlines = [SiswaInline]

    fieldsets = (
        (
            "Akun & Identitas",
            {
                "fields": ("user", "nama_lengkap", "nip"),
            },
        ),
        (
            "Data Pembimbing",
            {
                "fields": ("jabatan", "no_hp", "is_active"),
            },
        ),
    )

    @admin.display(description="Email", ordering="user__email")
    def get_email(self, obj):
        return obj.user.email

    @admin.display(description="Status")
    def status_badge(self, obj):
        if obj.is_active:
            return mark_safe(
                '<span style="background:#EAF3DE;color:#3B6D11;padding:2px 10px;'
                'border-radius:10px;font-size:12px;font-weight:500">Aktif</span>'
            )
        return mark_safe(
            '<span style="background:#F1EFE8;color:#5F5E5A;padding:2px 10px;'
            'border-radius:10px;font-size:12px;font-weight:500">Nonaktif</span>'
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user")
            .prefetch_related("siswa_set")
        )


@admin.register(Siswa)
class SiswaAdmin(admin.ModelAdmin):
    list_display = (
        "nama_lengkap",
        "nis",
        "jurusan",
        "angkatan",
        "pembimbing",
        "tahun_ajaran",
        "get_email",
        "status_badge",
    )
    list_filter = ("is_active", "jurusan", "tahun_ajaran", "angkatan", "pembimbing")
    search_fields = ("nama_lengkap", "nis", "user__email", "user__username")
    ordering = ("nama_lengkap",)
    list_per_page = 25
    autocomplete_fields = ["user"]

    fieldsets = (
        (
            "Akun & Identitas",
            {
                "fields": ("user", "nama_lengkap", "nis"),
            },
        ),
        (
            "Data Akademik",
            {
                "fields": ("jurusan", "tahun_ajaran", "angkatan", "pembimbing"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_active",),
            },
        ),
    )

    @admin.display(description="Email", ordering="user__email")
    def get_email(self, obj):
        return obj.user.email

    @admin.display(description="Status")
    def status_badge(self, obj):
        if obj.is_active:
            return mark_safe(
                '<span style="background:#EAF3DE;color:#3B6D11;padding:2px 10px;'
                'border-radius:10px;font-size:12px;font-weight:500">Aktif</span>'
            )
        return mark_safe(
            '<span style="background:#F1EFE8;color:#5F5E5A;padding:2px 10px;'
            'border-radius:10px;font-size:12px;font-weight:500">Nonaktif</span>'
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "jurusan", "tahun_ajaran", "pembimbing")
        )

    actions = ["nonaktifkan_siswa", "aktifkan_siswa"]

    @admin.action(description="Nonaktifkan siswa terpilih")
    def nonaktifkan_siswa(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} siswa berhasil dinonaktifkan.")

    @admin.action(description="Aktifkan siswa terpilih")
    def aktifkan_siswa(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} siswa berhasil diaktifkan.")