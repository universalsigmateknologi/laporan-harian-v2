from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from master.models import TahunAjaran
from siswa.models import Siswa


class LaporanHarian(models.Model):
    """
    Inti aplikasi — rekap kegiatan harian setiap siswa.
    Alur status: draft → submitted → approved / revisi → submitted (ulang)
    """

    class Status(models.TextChoices):
        DALAM_PROSES = "Dalam Proses", "Dalam Proses"
        SELESAI = "Selesai", "Selesai"

    siswa = models.ForeignKey(
        Siswa,
        on_delete=models.CASCADE,
        related_name="laporan_harian",
        verbose_name="Siswa",
    )
    tahun_ajaran = models.ForeignKey(
        TahunAjaran,
        on_delete=models.PROTECT,
        related_name="laporan_harian",
        verbose_name="Tahun Ajaran",
    )
    uraian_pekerjaan = models.TextField(verbose_name="Uraian Pekerjaan")
    hasil_progress = models.TextField(verbose_name="Hasil / Progress")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DALAM_PROSES,
        verbose_name="Status",
    )
    tanggal = models.DateField(verbose_name="Tanggal Kegiatan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Diperbarui")

    class Meta:
        verbose_name = "Laporan Harian"
        verbose_name_plural = "Laporan Harian"
        ordering = ["-tanggal", "-created_at"]
        unique_together = (("siswa", "tanggal"),)

    def __str__(self):
        return f"{self.siswa.nama_lengkap} — {self.created_at:%d %b %Y}"

    @property
    def is_editable(self):
        return True

    @property
    def jumlah_foto(self):
        return self.foto_bukti.count()

    def save(self, *args, **kwargs):
        # Ensure `tanggal` is populated (historic migrations expect this column)
        if not getattr(self, "tanggal", None):
            # Prefer created_at date if already set, otherwise use now().date()
            if self.created_at:
                try:
                    self.tanggal = self.created_at.date()
                except Exception:
                    self.tanggal = timezone.now().date()
            else:
                self.tanggal = timezone.now().date()
        super().save(*args, **kwargs)


def foto_upload_path(instance, filename):
    """
    Simpan foto bukti ke folder terstruktur:
    foto_bukti/YYYY/MM/nis_siswa/filename
    """
    today = timezone.now()
    nis = instance.laporan.siswa.nis
    return f"foto_bukti/{today.year}/{today.month:02d}/{nis}/{filename}"


class FotoBukti(models.Model):
    """
    Foto bukti kegiatan untuk setiap laporan harian.
    Satu laporan bisa punya banyak foto.
    """

    laporan = models.ForeignKey(
        LaporanHarian,
        on_delete=models.CASCADE,
        related_name="foto_bukti",
        verbose_name="Laporan Harian",
    )
    foto = models.ImageField(
        upload_to=foto_upload_path,
        verbose_name="Foto Bukti",
    )
    keterangan = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Keterangan Foto",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Diunggah")

    class Meta:
        verbose_name = "Foto Bukti"
        verbose_name_plural = "Foto Bukti"
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"Foto untuk {self.laporan} — {self.uploaded_at:%d/%m/%Y %H:%M}"