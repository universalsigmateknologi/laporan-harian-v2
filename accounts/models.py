from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model untuk aplikasi MEDESKA.
    Ada 3 role: admin, siswa, dan pembimbing.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        SISWA = "siswa", "Siswa"
        KEPALA_SEKOLAH = "kepala_sekolah", "Kepala Sekolah"
        PEMBIMBING = "pembimbing", "Pembimbing"

    role = models.CharField(
        max_length=15,
        choices=Role.choices,
        default=Role.SISWA,
        verbose_name="Role",
    )

    # Override email agar unik dan wajib diisi
    email = models.EmailField(unique=True, verbose_name="Email", blank=True, null=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["role"]

    class Meta:
        verbose_name = "Pengguna"
        verbose_name_plural = "Pengguna"
        ordering = ["username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_siswa(self):
        return self.role == self.Role.SISWA

    @property
    def is_kepala_sekolah(self):
        return self.role == self.Role.KEPALA_SEKOLAH

    @property
    def is_pembimbing(self):
        return self.role == self.Role.PEMBIMBING