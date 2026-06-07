from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Jurusan, TahunAjaran


@admin.register(Jurusan)
class JurusanAdmin(admin.ModelAdmin):
    list_display = ("kode", "nama", "status_badge", "jumlah_siswa_aktif")
    list_filter = ("is_active",)
    search_fields = ("nama", "kode")
    ordering = ("nama",)
    list_per_page = 25

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

    @admin.display(description="Jumlah Siswa")
    def jumlah_siswa_aktif(self, obj):
        # Hindari ImportError sirkular — import di dalam method
        count = obj.siswa_set.filter(is_active=True).count()
        return count

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("siswa_set")


@admin.register(TahunAjaran)
class TahunAjaranAdmin(admin.ModelAdmin):
    list_display = ("nama", "status_aktif_badge", "jumlah_siswa", "jumlah_laporan")
    list_filter = ("is_aktif",)
    search_fields = ("nama",)
    ordering = ("-nama",)
    list_per_page = 25

    @admin.display(description="Status", boolean=False)
    def status_aktif_badge(self, obj):
        if obj.is_aktif:
            return mark_safe(
                '<span style="background:#E6F1FB;color:#0C447C;padding:2px 10px;'
                'border-radius:10px;font-size:12px;font-weight:500">Tahun Aktif</span>'
            )
        return mark_safe(
            '<span style="background:#F1EFE8;color:#5F5E5A;padding:2px 10px;'
            'border-radius:10px;font-size:12px;font-weight:500">Tidak Aktif</span>'
        )

    @admin.display(description="Jumlah Siswa")
    def jumlah_siswa(self, obj):
        return obj.siswa_set.filter(is_active=True).count()

    @admin.display(description="Jumlah Laporan")
    def jumlah_laporan(self, obj):
        return obj.laporan_harian.count()

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("siswa_set", "laporan_harian")
        )

    def save_model(self, request, obj, form, change):
        """
        Override save_model agar logika deaktivasi tahun ajaran lain
        tetap berjalan melalui method save() di model.
        """
        super().save_model(request, obj, form, change)

    actions = ["set_aktif"]

    @admin.action(description="Jadikan tahun ajaran ini aktif")
    def set_aktif(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "Hanya boleh memilih satu tahun ajaran untuk diaktifkan.",
                level="error",
            )
            return
        obj = queryset.first()
        obj.is_aktif = True
        obj.save()
        self.message_user(
            request,
            f"Tahun ajaran {obj.nama} berhasil diaktifkan.",
        )