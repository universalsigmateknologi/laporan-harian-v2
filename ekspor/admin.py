from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import LogEkspor


@admin.register(LogEkspor)
class LogEksporAdmin(admin.ModelAdmin):
    """
    Log ekspor bersifat read-only — tidak ada yang boleh diedit atau ditambah
    secara manual dari panel admin. Record dibuat otomatis oleh sistem
    setiap kali file DOCX/PDF digenerate dari views.
    """

    list_display = (
        "created_at",
        "get_digenerate_oleh",
        "get_nama_siswa",
        "format_badge",
        "rentang_mulai",
        "rentang_selesai",
        "link_unduh",
    )
    list_filter = ("format", "created_at", "siswa__jurusan", "siswa__tahun_ajaran")
    search_fields = (
        "digenerate_oleh__username",
        "digenerate_oleh__email",
        "siswa__nama_lengkap",
        "siswa__nis",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 30

    readonly_fields = (
        "digenerate_oleh",
        "siswa",
        "format",
        "rentang_mulai",
        "rentang_selesai",
        "file_path",
        "created_at",
        "link_unduh",
    )

    fieldsets = (
        (
            "Informasi Ekspor",
            {
                "fields": (
                    "digenerate_oleh",
                    "siswa",
                    "format",
                    "rentang_mulai",
                    "rentang_selesai",
                ),
            },
        ),
        (
            "File",
            {
                "fields": ("file_path", "link_unduh", "created_at"),
            },
        ),
    )

    @admin.display(description="Oleh", ordering="digenerate_oleh__username")
    def get_digenerate_oleh(self, obj):
        if obj.digenerate_oleh:
            return obj.digenerate_oleh.get_full_name() or obj.digenerate_oleh.username
        return mark_safe('<span style="color:#888780">—</span>')

    @admin.display(description="Siswa", ordering="siswa__nama_lengkap")
    def get_nama_siswa(self, obj):
        if obj.siswa:
            return obj.siswa.nama_lengkap
        return mark_safe(
            '<span style="background:#EEEDFE;color:#3C3489;padding:2px 8px;'
            'border-radius:10px;font-size:12px;font-weight:500">Semua Siswa</span>'
        )

    @admin.display(description="Format")
    def format_badge(self, obj):
        style_map = {
            LogEkspor.Format.DOCX: ("#E6F1FB", "#0C447C", "DOCX"),
            LogEkspor.Format.PDF:  ("#FAECE7", "#712B13", "PDF"),
        }
        bg, fg, label = style_map.get(obj.format, ("#F1EFE8", "#5F5E5A", obj.format.upper()))
        return format_html(
            '<span style="background:{bg};color:{fg};padding:2px 10px;'
            'border-radius:10px;font-size:12px;font-weight:500">{label}</span>',
            bg=bg, fg=fg, label=label,
        )

    @admin.display(description="Unduh File")
    def link_unduh(self, obj):
        if obj.file_path:
            return format_html(
                '<a href="{url}" target="_blank" style="'
                "color:#185FA5;font-size:12px;text-decoration:none;"
                'font-weight:500">Unduh &rarr;</a>',
                url=obj.file_path.url,
            )
        return mark_safe('<span style="color:#888780">File tidak tersedia</span>')

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("digenerate_oleh", "siswa", "siswa__jurusan", "siswa__tahun_ajaran")
        )

    # Larang tambah & ubah record dari panel admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # Izinkan hapus hanya untuk superuser (bersihkan file lama)
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser