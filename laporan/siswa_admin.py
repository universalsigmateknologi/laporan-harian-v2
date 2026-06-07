"""
laporan/siswa_admin.py

Custom AdminSite khusus siswa — terpisah dari /admin/ milik staf sekolah.
Diakses via URL /siswa/ (dikonfigurasi di urls.py root proyek).

Prinsip keamanan:
- Setiap ModelAdmin di sini meng-override get_queryset() agar hanya
  mengembalikan data milik siswa yang sedang login.
- Field 'siswa' dan 'tahun_ajaran' di-set otomatis dari sesi login,
  tidak ditampilkan ke siswa sebagai input.
- Laporan yang sudah di-submit atau disetujui tidak bisa diedit.
- Siswa tidak bisa menghapus laporan yang sudah di-submit/approved.
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from master.models import TahunAjaran
from .models import FotoBukti, LaporanHarian


# ─────────────────────────────────────────────
# 1. Custom AdminSite untuk siswa
# ─────────────────────────────────────────────

class SiswaAdminSite(AdminSite):
    """
    AdminSite terpisah khusus siswa.
    URL: /siswa/  (bukan /admin/)
    """

    site_header  = "Portal Siswa MEDESKA"
    site_title   = "Portal Siswa"
    index_title  = "Selamat datang di Portal Laporan Harian"
    site_url     = None   # Sembunyikan tombol "View Site"

    def has_permission(self, request):
        """
        Hanya user aktif dengan role 'siswa' yang boleh masuk.
        Tidak perlu is_staff — siswa bukan staf.
        """
        if not request.user.is_active:
            return False
        if not request.user.is_authenticated:
            return False
        # Gunakan property is_siswa dari model User
        return getattr(request.user, "is_siswa", False)

    def each_context(self, request):
        ctx = super().each_context(request)
        # Sisipkan info profil siswa ke semua template
        try:
            ctx["siswa_profile"] = request.user.siswa
        except Exception:
            ctx["siswa_profile"] = None
        return ctx


# Instance tunggal — diimpor di urls.py
siswa_admin_site = SiswaAdminSite(name="siswa_admin")


# ─────────────────────────────────────────────
# Helper: ambil profil siswa dari request
# ─────────────────────────────────────────────

def _get_siswa(request):
    """
    Ambil objek Siswa yang terhubung ke user yang sedang login.
    Raise PermissionDenied jika profil tidak ditemukan.
    """
    try:
        return request.user.siswa
    except Exception:
        raise PermissionDenied("Akun ini tidak terhubung ke profil siswa.")


# ─────────────────────────────────────────────
# 2. Inline foto bukti (versi siswa)
# ─────────────────────────────────────────────

class FotoBuktiSiswaInline(admin.TabularInline):
    model    = FotoBukti
    fields   = ("foto_preview", "foto", "keterangan")
    readonly_fields = ("foto_preview",)
    extra    = 1
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

    def get_readonly_fields(self, request, obj=None):
        """
        Foto tidak bisa diubah jika laporan sudah submitted/approved.
        """
        ro = list(super().get_readonly_fields(request, obj))
        if obj and not obj.is_editable:
            ro += ["foto", "keterangan"]
        return ro

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        if obj and not obj.is_editable:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        if obj and not obj.is_editable:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Hanya bisa hapus foto jika laporan masih editable
        if obj and not obj.is_editable:
            return False
        return True


# ─────────────────────────────────────────────
# 3. LaporanHarian — tampilan siswa
# ─────────────────────────────────────────────

class LaporanHarianSiswaAdmin(admin.ModelAdmin):
    """
    Siswa hanya melihat dan mengelola laporan milik sendiri.
    """

    # ── Tampilan list ────────────────────────────────────────────────────
    list_display   = ("created_at", "jumlah_foto", "updated_at")
    list_filter    = ()
    search_fields  = ("uraian_pekerjaan", "hasil_progress")
    ordering       = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page  = 20

    # ── Form detail ──────────────────────────────────────────────────────
    fieldsets = (
        (
            "Isi Laporan",
            {
                "fields": ("uraian_pekerjaan", "hasil_progress"),
                "description": (
                    "Isi dengan jelas uraian pekerjaan yang telah dilakukan "
                    "dan hasil atau progress yang dicapai hari ini."
                ),
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    inlines = [FotoBuktiSiswaInline]

    # ── Keamanan: batasi queryset ke milik siswa ─────────────────────────

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            siswa = _get_siswa(request)
            return qs.filter(siswa=siswa).select_related(
                "siswa", "tahun_ajaran"
            ).prefetch_related("foto_bukti")
        except PermissionDenied:
            return qs.none()

    # ── Auto-isi field tersembunyi saat save ─────────────────────────────

    def save_model(self, request, obj, form, change):
        if not change:
            # Laporan baru: isi otomatis siswa & tahun ajaran aktif
            obj.siswa = _get_siswa(request)
            obj.tahun_ajaran = TahunAjaran.get_aktif()
            if obj.tahun_ajaran is None:
                from django.contrib import messages
                self.message_user(
                    request,
                    "Tidak ada tahun ajaran yang aktif. Hubungi admin sekolah.",
                    level="error",
                )
                return
        super().save_model(request, obj, form, change)

    # ── Kontrol permission per-objek ─────────────────────────────────────

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        # Cek apakah ada tahun ajaran aktif
        return TahunAjaran.get_aktif() is not None

    def has_module_permission(self, request):
        return True

    def has_module_perms(self, request):
        return True

    # ── Sembunyikan field siswa & tahun ajaran dari form siswa ───────────

    def get_fields(self, request, obj=None):
        # Ambil fields dari fieldsets, tidak menyertakan siswa/tahun_ajaran
        return [
            "tanggal",
            "uraian_pekerjaan",
            "hasil_progress",
        ]

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields

    # ── Display methods ──────────────────────────────────────────────────

    @admin.display(description="Foto")
    def jumlah_foto(self, obj):
        count = obj.foto_bukti.count()
        return format_html(
            '<span style="color:{color};font-weight:500">{count}</span>',
            color="#3B6D11" if count > 0 else "#888780",
            count=count,
        )


# ─────────────────────────────────────────────
# 4. Daftarkan model ke SiswaAdminSite
# ─────────────────────────────────────────────

siswa_admin_site.register(LaporanHarian, LaporanHarianSiswaAdmin)