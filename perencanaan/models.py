from django.db import models
from master.models import Jurusan
from siswa.models import Siswa

class KategoriPerencanaan(models.Model):
    siswa = models.ForeignKey(
        Siswa,
        on_delete=models.CASCADE,
        related_name="kategori_perencanaan_set",
        verbose_name="Siswa",
        null=True,
        blank=True,
    )

    nama = models.CharField(max_length=100, verbose_name="Nama Kategori")
    keterangan = models.TextField(blank=True, verbose_name="Keterangan")

    class Meta:
        verbose_name = "Kategori Perencanaan"
        verbose_name_plural = "Kategori Perencanaan"
        constraints = [
            models.UniqueConstraint(fields=["siswa", "nama"], name="unique_kategori_per_siswa"),
        ]

    def __str__(self):
        return self.nama


class Client(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nama Client")
    bidang = models.ManyToManyField(Jurusan, related_name="clients", verbose_name="Bidang / Jurusan")
    instansi = models.CharField(max_length=200, verbose_name="Instansi")
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    telp = models.CharField(max_length=20, verbose_name="No. Telp", blank=True, null=True)

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Client"

    def __str__(self):
        return f"{self.name} ({self.instansi})"

class Perencanaan(models.Model):
    kategori = models.ForeignKey(
        KategoriPerencanaan, 
        on_delete=models.PROTECT, 
        related_name="perencanaan_set",
        verbose_name="Kategori Perencanaan"
    )
    siswa = models.ForeignKey(
        Siswa, 
        on_delete=models.CASCADE, 
        related_name="perencanaan_set",
        verbose_name="Siswa"
    )
    program = models.TextField(verbose_name="KategoriPerencanaanProgram")
    kegiatan = models.TextField(verbose_name="Kegiatan")
    indikator_pencapaian = models.TextField(verbose_name="Indikator Pencapaian")
    client = models.ForeignKey(
        Client, 
        on_delete=models.PROTECT, 
        related_name="perencanaan_set",
        verbose_name="Client / Sasaran"
    )
    waktu = models.DateField(verbose_name="Waktu / Tanggal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perencanaan"
        verbose_name_plural = "Perencanaan"
        ordering = ["-waktu", "-created_at"]

    def __str__(self):
        return f"{self.program} - {self.siswa.nama_lengkap}"
