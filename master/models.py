from django.db import models


class Jurusan(models.Model):
    """
    Data master jurusan siswa.
    Contoh: RPL, DKV, TKJ, MM, dll.
    """

    nama = models.CharField(max_length=100, unique=True, verbose_name="Nama Jurusan")
    kode = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Kode Jurusan",
        help_text="Singkatan jurusan, contoh: RPL, DKV",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Jurusan"
        verbose_name_plural = "Jurusan"
        ordering = ["nama"]

    def __str__(self):
        return f"{self.kode} - {self.nama}"


class TahunAjaran(models.Model):
    """
    Data master tahun ajaran.
    Hanya satu tahun ajaran yang boleh aktif pada satu waktu.
    Contoh: 2025/2026
    """

    nama = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Tahun Ajaran",
        help_text="Format: 2025/2026",
    )
    is_aktif = models.BooleanField(
        default=False,
        verbose_name="Tahun Ajaran Aktif",
        help_text="Hanya satu tahun ajaran yang boleh aktif",
    )

    class Meta:
        verbose_name = "Tahun Ajaran"
        verbose_name_plural = "Tahun Ajaran"
        ordering = ["-nama"]

    def __str__(self):
        return self.nama

    def save(self, *args, **kwargs):
        # Pastikan hanya satu tahun ajaran yang aktif
        if self.is_aktif:
            TahunAjaran.objects.exclude(pk=self.pk).update(is_aktif=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_aktif(cls):
        """Kembalikan tahun ajaran yang sedang aktif, atau None."""
        return cls.objects.filter(is_aktif=True).first()