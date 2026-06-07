"""
laporan/pembimbing_admin.py

Custom AdminSite khusus pembimbing — terpisah dari /admin/ dan /siswa/.
Diakses via URL /pembimbing/ (dikonfigurasi di urls.py root proyek).

Prinsip keamanan:
- Setiap ModelAdmin di sini meng-override get_queryset() agar hanya
  mengembalikan laporan dari siswa binaan pembimbing yang sedang login.
- Pembimbing hanya bisa MELIHAT laporan (read-only).
- Tidak bisa menambah, mengedit, atau menghapus laporan.
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html

from .models import FotoBukti, LaporanHarian


# ─────────────────────────────────────────────
# 1. Custom AdminSite untuk pembimbing
# ─────────────────────────────────────────────

class PembimbingAdminSite(AdminSite):
    """
    AdminSite terpisah khusus pembimbing.
    URL: /pembimbing/  (bukan /admin/ atau /siswa/)
    """

    site_header  = "Portal Pembimbing MEDESKA"
    site_title   = "Portal Pembimbing"
    index_title  = "Selamat datang di Portal Pembimbing"
    site_url     = None   # Sembunyikan tombol "View Site"

    def has_permission(self, request):
        """
        Hanya user aktif dengan role 'pembimbing' yang boleh masuk.
        Tidak perlu is_staff — pembimbing bukan staf.
        """
        if not request.user.is_active:
            return False
        if not request.user.is_authenticated:
            return False
        # Gunakan property is_pembimbing dari model User
        return getattr(request.user, "is_pembimbing", False)

    def each_context(self, request):
        ctx = super().each_context(request)
        # Sisipkan info profil pembimbing ke semua template
        try:
            ctx["pembimbing_profile"] = request.user.pembimbing
        except Exception:
            ctx["pembimbing_profile"] = None
        return ctx


# Instance tunggal — diimpor di urls.py
pembimbing_admin_site = PembimbingAdminSite(name="pembimbing_admin")


# ─────────────────────────────────────────────
# Helper: ambil profil pembimbing dari request
# ─────────────────────────────────────────────

def _get_pembimbing(request):
    """
    Ambil objek Pembimbing yang terhubung ke user yang sedang login.
    Raise PermissionDenied jika profil tidak ditemukan.
    """
    try:
        return request.user.pembimbing
    except Exception:
        raise PermissionDenied("Akun ini tidak terhubung ke profil pembimbing.")


# ─────────────────────────────────────────────
# 2. Inline foto bukti (read-only untuk pembimbing)
# ─────────────────────────────────────────────

class FotoBuktiPembimbingInline(admin.TabularInline):
    model    = FotoBukti
    fields   = ("foto_preview", "keterangan", "uploaded_at")
    readonly_fields = ("foto_preview", "keterangan", "uploaded_at")
    extra    = 0
    can_delete = False
    verbose_name       = "Foto Bukti"
    verbose_name_plural = "Foto Bukti Kegiatan"

    @admin.display(description="Preview")
    def foto_preview(self, obj):
        if obj.pk and obj.foto:
            return format_html(
                '<img src="{}" style="height:64px;width:auto;'
                'border-radius:6px;object-fit:cover;" />',
                obj.foto.url,
            )
        return "—"

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────
# 3. LaporanHarian — tampilan pembimbing (read-only)
# ─────────────────────────────────────────────

class LaporanHarianPembimbingAdmin(admin.ModelAdmin):
    """
    Pembimbing hanya bisa MELIHAT laporan dari siswa binaan.
    Semua aksi create/edit/delete dinonaktifkan.
    """

    # ── Tampilan list ────────────────────────────────────────────────────
    list_display   = (
        "created_at",
        "get_nama_siswa",
        "get_jurusan",
        "jumlah_foto",
        "updated_at",
    )
    list_filter    = ("created_at",)
    search_fields  = (
        "siswa__nama_lengkap",
        "siswa__nis",
        "uraian_pekerjaan",
        "hasil_progress",
    )
    ordering       = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page  = 20

    # ── Form detail (read-only) ──────────────────────────────────────────
    fieldsets = (
        (
            "Informasi Siswa",
            {
                "fields": ("get_nama_siswa_detail", "get_jurusan_detail", "get_nis_detail"),
            },
        ),
        (
            "Isi Laporan",
            {
                "fields": ("uraian_pekerjaan", "hasil_progress"),
            },
        ),
        (
            "Timestamp",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = (
        "uraian_pekerjaan",
        "hasil_progress",
        "created_at",
        "updated_at",
        "get_nama_siswa_detail",
        "get_jurusan_detail",
        "get_nis_detail",
    )

    inlines = [FotoBuktiPembimbingInline]

    # ── Keamanan: batasi queryset ke siswa binaan ────────────────────────

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            pembimbing = _get_pembimbing(request)
            return qs.filter(siswa__pembimbing=pembimbing).select_related(
                "siswa", "siswa__jurusan", "tahun_ajaran"
            ).prefetch_related("foto_bukti")
        except PermissionDenied:
            return qs.none()

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        # Return True agar bisa masuk halaman detail (view),
        # tapi semua field sudah readonly
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return True

    def has_module_perms(self, request):
        return True

    # ── Display methods ──────────────────────────────────────────────────

    @admin.display(description="Nama Siswa", ordering="siswa__nama_lengkap")
    def get_nama_siswa(self, obj):
        return obj.siswa.nama_lengkap

    @admin.display(description="Jurusan", ordering="siswa__jurusan__kode")
    def get_jurusan(self, obj):
        return obj.siswa.jurusan.kode

    @admin.display(description="Foto")
    def jumlah_foto(self, obj):
        count = obj.foto_bukti.count()
        return format_html(
            '<span style="color:{color};font-weight:500">{count}</span>',
            color="#3B6D11" if count > 0 else "#888780",
            count=count,
        )

    # ── Detail display methods (untuk form detail) ───────────────────────

    @admin.display(description="Nama Siswa")
    def get_nama_siswa_detail(self, obj):
        return obj.siswa.nama_lengkap

    @admin.display(description="Jurusan")
    def get_jurusan_detail(self, obj):
        return obj.siswa.jurusan.kode

    @admin.display(description="NIS")
    def get_nis_detail(self, obj):
        return obj.siswa.nis


# ─────────────────────────────────────────────
# 4. Daftarkan model ke PembimbingAdminSite
# ─────────────────────────────────────────────

pembimbing_admin_site.register(LaporanHarian, LaporanHarianPembimbingAdmin)
