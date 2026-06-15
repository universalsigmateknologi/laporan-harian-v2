from django.contrib import admin
from .models import KategoriPerencanaan, Client, Perencanaan, Program


@admin.register(KategoriPerencanaan)
class KategoriPerencanaanAdmin(admin.ModelAdmin):
    list_display = ('nama', 'keterangan')
    search_fields = ('nama',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'instansi', 'email', 'telp')
    search_fields = ('name', 'instansi', 'email')
    filter_horizontal = ('bidang',)

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("nama", "deskripsi", "siswa_user")
    search_fields = ("nama", "deskripsi")




@admin.register(Perencanaan)
class PerencanaanAdmin(admin.ModelAdmin):
    list_display = ("program", "siswa", "kegiatan", "client", "waktu")
    list_filter = ("kategori", "waktu", "siswa__jurusan")
    search_fields = ("program", "kegiatan", "siswa__nama_lengkap", "client__name")
    date_hierarchy = 'waktu'

