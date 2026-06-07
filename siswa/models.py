from django.db import models

from accounts.models import User
from master.models import Jurusan, TahunAjaran


class Pembimbing(models.Model):
    """
    Profil pembimbing yang terhubung ke akun User.
    Relasi OneToOne ke User sehingga satu akun = satu pembimbing.
    Satu pembimbing bisa membimbing banyak siswa.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pembimbing",
        verbose_name="Akun User",
        limit_choices_to={"role": User.Role.PEMBIMBING},
    )
    nama_lengkap = models.CharField(max_length=150, verbose_name="Nama Lengkap")
    nip = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="NIP",
        help_text="Nomor Induk Pegawai",
    )
    jabatan = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Jabatan",
    )
    no_hp = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="No. HP",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Pembimbing"
        verbose_name_plural = "Pembimbing"
        ordering = ["nama_lengkap"]

    def __str__(self):
        return self.nama_lengkap

    def jumlah_siswa(self):
        return self.siswa_set.filter(is_active=True).count()

    jumlah_siswa.short_description = "Jumlah Siswa"


class Siswa(models.Model):
    """
    Profil siswa yang terhubung ke akun User.
    Relasi OneToOne ke User sehingga satu akun = satu siswa.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="siswa",
        verbose_name="Akun User",
        limit_choices_to={"role": User.Role.SISWA},
    )
    pembimbing = models.ForeignKey(
        Pembimbing,
        on_delete=models.PROTECT,
        related_name="siswa_set",
        verbose_name="Pembimbing",
    )
    jurusan = models.ForeignKey(
        Jurusan,
        on_delete=models.PROTECT,
        related_name="siswa_set",
        verbose_name="Jurusan",
    )
    tahun_ajaran = models.ForeignKey(
        TahunAjaran,
        on_delete=models.PROTECT,
        related_name="siswa_set",
        verbose_name="Tahun Ajaran",
    )
    nama_lengkap = models.CharField(max_length=150, verbose_name="Nama Lengkap")
    nis = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="NIS",
        help_text="Nomor Induk Siswa",
    )
    angkatan = models.CharField(
        max_length=10,
        verbose_name="Angkatan",
        help_text="Tahun masuk, contoh: 2024",
    )
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Siswa"
        verbose_name_plural = "Siswa"
        ordering = ["nama_lengkap"]

    def __str__(self):
        return f"{self.nama_lengkap} ({self.nis})"

    @property
    def jurusan_kode(self):
        return self.jurusan.kode

    @property
    def nama_pembimbing(self):
        return self.pembimbing.nama_lengkap