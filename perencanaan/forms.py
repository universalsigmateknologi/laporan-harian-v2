from django import forms
from .models import Perencanaan, Client, KategoriPerencanaan, Program


class PerencanaanForm(forms.ModelForm):
    class Meta:
        model = Perencanaan
        fields = [
            "siswa",
            "kategori",
            "program",
            "kegiatan",
            "indikator_pencapaian",
            "client",
            "waktu",
        ]
        widgets = {
            "waktu": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none",
                }
            ),
            "siswa": forms.Select(
                attrs={
                    "class": "form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none bg-white"
                }
            ),
            "kategori": forms.Select(
                attrs={
                    "class": "form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none bg-white"
                }
            ),
            "client": forms.Select(
                attrs={
                    "class": "form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none bg-white"
                }
            ),
            "program": forms.Select(
                attrs={
                    "class": "form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none bg-white"
                }
            ),
            "kegiatan": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-input w-full rounded-2xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none",
                }
            ),
            "indikator_pencapaian": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "form-input w-full rounded-2xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        show_siswa = kwargs.pop("show_siswa", False)
        siswa = kwargs.pop("siswa", None)
        super().__init__(*args, **kwargs)

        if not show_siswa:
            self.fields.pop("siswa")

        # Filter dropdown kategori agar hanya kategori milik siswa yang sedang login.
        if siswa is not None and "kategori" in self.fields:
            self.fields["kategori"].queryset = KategoriPerencanaan.objects.filter(siswa=siswa)

        # dropdown program (tanpa filter kategori, karena Program tidak lagi terikat kategori)
        if "program" in self.fields:
            self.fields["program"].queryset = Program.objects.all().order_by("nama")




class KategoriPerencanaanForm(forms.ModelForm):
    class Meta:
        model = KategoriPerencanaan
        fields = ["nama", "keterangan"]
        widgets = {
            "nama": forms.TextInput(
                attrs={
                    "class": "form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none",
                }
            ),
            "keterangan": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-input w-full rounded-2xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none",
                }
            ),
        }

