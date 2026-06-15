"""
urls.py (root proyek — biasanya di folder yang sama dengan settings.py)

Tiga AdminSite berjalan secara paralel:
  /admin/      → Django admin standar untuk staf/admin sekolah
  /siswa/      → Portal laporan harian khusus siswa
  /pembimbing/ → Portal pembimbing untuk melihat laporan siswa binaan
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import instance AdminSite yang sudah dikonfigurasi
from laporan.siswa_admin import siswa_admin_site
from laporan.pembimbing_admin import pembimbing_admin_site

urlpatterns = [
    # Admin sekolah (staf / superuser)
    path("admin/", admin.site.urls),

    # Portal siswa — AdminSite terpisah
    path("siswa/", siswa_admin_site.urls),

    # Portal pembimbing — AdminSite terpisah (read-only)
    path("pembimbing/", pembimbing_admin_site.urls, name="pembimbing"),
    path("", include("accounts.urls")),  # URL untuk aplikasi accounts
    path("laporan/", include("laporan.urls")),
    path("perencanaan/", include("perencanaan.urls")),
]

# Sajikan file media di mode development
if settings.local.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)