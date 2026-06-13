from django import forms
from .models import Perencanaan, Client, KategoriPerencanaan

class PerencanaanForm(forms.ModelForm):
    class Meta:
        model = Perencanaan
        fields = ['siswa', 'kategori', 'program', 'kegiatan', 'indikator_pencapaian', 'client', 'waktu']
        widgets = {
            'waktu': forms.DateInput(attrs={'type': 'date', 'class': 'form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none'}),
            'siswa': forms.Select(attrs={'class': 'form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none bg-white'}),
            'kategori': forms.Select(attrs={'class': 'form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none bg-white'}),
            'client': forms.Select(attrs={'class': 'form-input w-full rounded-xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none bg-white'}),
            'program': forms.Textarea(attrs={'rows': 3, 'class': 'form-input w-full rounded-2xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none'}),
            'kegiatan': forms.Textarea(attrs={'rows': 3, 'class': 'form-input w-full rounded-2xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none'}),
            'indikator_pencapaian': forms.Textarea(attrs={'rows': 3, 'class': 'form-input w-full rounded-2xl border border-navy-200 px-4 py-3 text-sm text-navy-900 focus:outline-none'}),
        }

    def __init__(self, *args, **kwargs):
        show_siswa = kwargs.pop('show_siswa', False)
        super().__init__(*args, **kwargs)
        if not show_siswa:
            self.fields.pop('siswa')
