from django.db import models

from accounts.models import User
from siswa.models import Siswa


def ekspor_upload_path(instance, filename):
    """
    Simpan file ekspor ke folder terstruktur:
    ekspor/YYYY/MM/format/filename
    """
    from django.utils import timezone

    today = timezone.now()
    return f"ekspor/{today.year}/{today.month:02d}/{instance.format}/{filename}"


class LogEkspor(models.Model):
    """
    Riwayat setiap file DOCX/PDF yang pernah digenerate.
    Berfungsi sebagai audit trail — siapa mengunduh apa dan kapan.
    """

    class Format(models.TextChoices):
        DOCX = "docx", "Microsoft Word (.docx)"
        PDF = "pdf", "PDF (.pdf)"

    digenerate_oleh = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="log_ekspor",
        verbose_name="Digenerate Oleh",
    )
    siswa = models.ForeignKey(
        Siswa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_ekspor",
        verbose_name="Siswa",
        help_text="Kosong jika ekspor semua siswa (laporan global admin)",
    )
    format = models.CharField(
        max_length=5,
        choices=Format.choices,
        verbose_name="Format File",
    )
    rentang_mulai = models.DateField(verbose_name="Dari Tanggal")
    rentang_selesai = models.DateField(verbose_name="Sampai Tanggal")
    file_path = models.FileField(
        upload_to=ekspor_upload_path,
        verbose_name="File",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Digenerate")

    class Meta:
        verbose_name = "Log Ekspor"
        verbose_name_plural = "Log Ekspor"
        ordering = ["-created_at"]

    def __str__(self):
        target = self.siswa.nama_lengkap if self.siswa else "Semua Siswa"
        return (
            f"[{self.get_format_display()}] {target} "
            f"({self.rentang_mulai} s/d {self.rentang_selesai}) "
            f"— {self.created_at:%d/%m/%Y %H:%M}"
        )

    @property
    def nama_file(self):
        """Kembalikan nama file saja tanpa path folder."""
        if self.file_path:
            return self.file_path.name.split("/")[-1]
        return "-"