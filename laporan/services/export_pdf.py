import base64
import io
from urllib.parse import urljoin

import qrcode
from django.template.loader import render_to_string
from django.urls import reverse
from weasyprint import HTML

from laporan.services.rekap import format_tanggal_short


def _build_qr_data_uri(url: str) -> str:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def generate_pdf(queryset, *, tahun_ajaran_nama: str = "", base_url: str = "") -> bytes:
    if base_url and not base_url.endswith("/"):
        base_url += "/"

    rows = []
    for index, laporan in enumerate(queryset, start=1):
        detail_url = urljoin(base_url, reverse("laporan:detail", args=[laporan.pk]))
        rows.append(
            {
                "no": index,
                "nama": laporan.siswa.nama_lengkap,
                "jurusan": laporan.siswa.jurusan.kode,
                "uraian": laporan.uraian_pekerjaan,
                "hasil": laporan.hasil_progress,
                "status": laporan.status,
                "tanggal": format_tanggal_short(laporan.tanggal),
                "qr_code": _build_qr_data_uri(detail_url),
            }
        )

    html = render_to_string(
        "laporan/export_pdf.html",
        {
            "rows": rows,
            "tahun_ajaran_nama": tahun_ajaran_nama,
            "total": len(rows),
        },
    )
    return HTML(string=html).write_pdf()
