from django.urls import path

from . import views

app_name = "laporan"

urlpatterns = [
    path("tambah/", views.laporan_post, name="laporan_post"),
    path("edit/<int:pk>/", views.laporan_edit, name="laporan_edit"),
    path("rekap/", views.rekap_harian, name="rekap_harian"),
    path("rekap/<int:pk>/", views.laporan_detail, name="detail"),
    path("rekap/export/pdf/", views.export_pdf, name="export_pdf"),
    path("rekap/export/excel/", views.export_excel, name="export_excel"),
]
