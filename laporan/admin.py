from django.contrib import admin
from django.utils.html import format_html, mark_safe

from .models import FotoBukti, LaporanHarian


class FotoBuktiInline(admin.TabularInline):
    """
    Tampilkan foto bukti langsung di dalam halaman detail LaporanHarian.
    Admin bisa melihat preview thumbnail dan menghapus foto.
    """

    model = FotoBukti
    fields = ("foto_preview", "foto", "keterangan", "uploaded_at")
    readonly_fields = ("foto_preview", "uploaded_at")
    extra = 0
    verbose_name = "Foto Bukti"
    verbose_name_plural = "Foto Bukti Kegiatan"

    @admin.display(description="Preview")
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="height:60px;width:auto;'
                'border-radius:4px;object-fit:cover;" />',
                obj.foto.url,
            )
        return "-"


@admin.register(LaporanHarian)
class LaporanHarianAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "get_nama_siswa",
        "get_jurusan",
        "status",
        "get_pembimbing",
        "jumlah_foto",
        "updated_at",
    )
    list_filter = (
        "status",
        "tahun_ajaran",
        "siswa__jurusan",
        "siswa__pembimbing",
        "created_at",
    )
    search_fields = (
        "siswa__nama_lengkap",
        "siswa__nis",
        "uraian_pekerjaan",
        "hasil_progress",
    )
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 30
    inlines = [FotoBuktiInline]

    fieldsets = (
        (
            "Informasi Laporan",
            {
                "fields": ("siswa", "tahun_ajaran"),
            },
        ),
        (
            "Isi Laporan",
            {
                "fields": ("uraian_pekerjaan", "hasil_progress", "status"),
            },
        ),
        (
            "Timestamp",
            {
                "fields": ("created_at", "updated_at"),
                # "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("updated_at",)

    @admin.display(description="Nama Siswa", ordering="siswa__nama_lengkap")
    def get_nama_siswa(self, obj):
        return obj.siswa.nama_lengkap

    @admin.display(description="Jurusan", ordering="siswa__jurusan__kode")
    def get_jurusan(self, obj):
        return obj.siswa.jurusan.kode

    @admin.display(description="Pembimbing", ordering="siswa__pembimbing__nama_lengkap")
    def get_pembimbing(self, obj):
        return obj.siswa.pembimbing.nama_lengkap

    @admin.display(description="Foto")
    def jumlah_foto(self, obj):
        count = obj.foto_bukti.count()
        if count == 0:
            return mark_safe(
                '<span style="color:#888780">0</span>'
            )
        return format_html(
            '<span style="font-weight:500">{}</span>', count
        )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "siswa",
                "siswa__jurusan",
                "siswa__pembimbing",
                "tahun_ajaran",
            )
            .prefetch_related("foto_bukti")
        )


@admin.register(FotoBukti)
class FotoBuktiAdmin(admin.ModelAdmin):
    """
    Admin FotoBukti terpisah — untuk keperluan pengelolaan file foto
    secara langsung (misalnya menghapus foto yang tidak sesuai).
    """

    list_display = (
        "foto_preview",
        "get_nama_siswa",
        "get_tanggal_laporan",
        "keterangan",
        "uploaded_at",
    )
    list_filter = ("laporan__siswa__jurusan", "uploaded_at")
    search_fields = (
        "laporan__siswa__nama_lengkap",
        "laporan__siswa__nis",
        "keterangan",
    )
    ordering = ("-uploaded_at",)
    list_per_page = 30
    readonly_fields = ("foto_preview_besar", "uploaded_at")

    fieldsets = (
        (
            "Informasi Foto",
            {
                "fields": ("laporan", "foto", "foto_preview_besar", "keterangan", "uploaded_at"),
            },
        ),
    )

    @admin.display(description="Preview")
    def foto_preview(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="height:48px;width:auto;'
                'border-radius:4px;object-fit:cover;" />',
                obj.foto.url,
            )
        return "-"

    @admin.display(description="Preview Besar")
    def foto_preview_besar(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height:300px;max-width:100%;'
                'border-radius:8px;object-fit:contain;" />',
                obj.foto.url,
            )
        return "-"

    @admin.display(description="Nama Siswa", ordering="laporan__siswa__nama_lengkap")
    def get_nama_siswa(self, obj):
        return obj.laporan.siswa.nama_lengkap

    @admin.display(description="Tanggal Laporan", ordering="laporan__created_at")
    def get_tanggal_laporan(self, obj):
        return obj.laporan.created_at.date()

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("laporan", "laporan__siswa", "laporan__siswa__jurusan")
        )