from datetime import date

from django.db.models import Q, QuerySet

from laporan.models import LaporanHarian
from master.models import Jurusan, TahunAjaran

PER_PAGE = 20

BULAN_ID = (
    "",
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember",
)
HARI_ID = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad")

STATUS_SLUG_MAP = {
    "dalam-proses": LaporanHarian.Status.DALAM_PROSES,
    "selesai": LaporanHarian.Status.SELESAI,
}

STATUS_LABELS = {
    "dalam-proses": "Dalam Proses",
    "selesai": "Selesai",
}


def get_tahun_ajaran_aktif():
    return TahunAjaran.get_aktif()


def get_jurusan_aktif():
    return Jurusan.objects.filter(is_active=True).order_by("kode")


def get_base_queryset(tahun_ajaran) -> QuerySet:
    if not tahun_ajaran:
        return LaporanHarian.objects.none()
    return (
        LaporanHarian.objects.filter(tahun_ajaran=tahun_ajaran)
        .select_related("siswa", "siswa__jurusan")
        .prefetch_related("foto_bukti")
        .order_by("-created_at", "siswa__nama_lengkap")
    )


def apply_filters(
    queryset: QuerySet,
    *,
    q: str = "",
    tanggal: str = "",
    jurusan: str = "",
    status: str = "",
    laporan_id: str = "",
) -> QuerySet:
    if laporan_id:
        try:
            queryset = queryset.filter(pk=int(laporan_id))
        except (TypeError, ValueError):
            pass
        return queryset
    if q:
        queryset = queryset.filter(
            Q(siswa__nama_lengkap__icontains=q) | Q(siswa__nis__icontains=q)
        )
    if tanggal:
        try:
            parsed = date.fromisoformat(tanggal)
        except ValueError:
            parsed = None
        if parsed:
            queryset = queryset.filter(created_at__date=parsed)
    if jurusan and jurusan != "semua":
        queryset = queryset.filter(siswa__jurusan__kode__iexact=jurusan)
    if status and status != "semua":
        status_value = STATUS_SLUG_MAP.get(status)
        if status_value:
            queryset = queryset.filter(status=status_value)
    return queryset


def get_rekap_stats(queryset: QuerySet) -> dict:
    total = queryset.count()
    dalam_proses = queryset.filter(
        status=LaporanHarian.Status.DALAM_PROSES
    ).count()
    selesai = queryset.filter(status=LaporanHarian.Status.SELESAI).count()
    jumlah_siswa = queryset.values("siswa").distinct().count()
    return {
        "total": total,
        "dalam_proses": dalam_proses,
        "selesai": selesai,
        "jumlah_siswa": jumlah_siswa,
    }


def get_tanggal_options(queryset: QuerySet) -> list[dict]:
    dates = (
        queryset.values_list("created_at__date", flat=True)
        .distinct()
        .order_by("-created_at__date")
    )
    return [
        {"value": d.isoformat(), "label": format_tanggal_label(d)}
        for d in dates
    ]


def format_tanggal_label(d: date) -> str:
    hari = HARI_ID[d.weekday()]
    bulan = BULAN_ID[d.month]
    return f"{hari}, {d.day} {bulan} {d.year}"


def format_tanggal_short(d: date) -> str:
    return f"{d.day} {BULAN_ID[d.month]} {d.year}"


def build_page_rows(page_object_list) -> list[dict]:
    """Nomor urut per tanggal (sesuai mockup HTML asli)."""
    rows = []
    prev_date = None
    row_num = 0
    for laporan in page_object_list:
        current_date = laporan.created_at.date()
        if current_date != prev_date:
            row_num = 1
            prev_date = current_date
        else:
            row_num += 1
        fotos = list(laporan.foto_bukti.all())
        foto_urls = [f.foto.url for f in fotos if f.foto]
        rows.append(
            {
                "laporan": laporan,
                "row_num": row_num,
                "fotos": fotos,
                "foto_urls": foto_urls,
                "foto_visible": fotos[:3],
                "foto_extra_count": max(0, len(fotos) - 3),
            }
        )
    return rows


def get_adjacent_laporan(filtered_qs: QuerySet, current_pk: int):
    """Laporan sebelum/sesudah dalam urutan daftar rekap (filter sama)."""
    laporan_list = list(filtered_qs)
    index = next((i for i, item in enumerate(laporan_list) if item.pk == current_pk), None)
    if index is None:
        return None, None
    prev_laporan = laporan_list[index - 1] if index > 0 else None
    next_laporan = laporan_list[index + 1] if index < len(laporan_list) - 1 else None
    return prev_laporan, next_laporan


def get_filter_labels(filters: dict) -> dict:
    labels = {}
    if filters.get("jurusan") and filters["jurusan"] != "semua":
        labels["jurusan"] = filters["jurusan"].upper()
    if filters.get("tanggal"):
        try:
            d = date.fromisoformat(filters["tanggal"])
            labels["tanggal"] = format_tanggal_short(d)
        except ValueError:
            labels["tanggal"] = filters["tanggal"]
    if filters.get("status") and filters["status"] != "semua":
        labels["status"] = STATUS_LABELS.get(
            filters["status"], filters["status"]
        )
    if filters.get("q"):
        labels["q"] = filters["q"]
    return labels


def has_active_filters(filters: dict) -> bool:
    return bool(
        filters.get("q")
        or (filters.get("jurusan") and filters["jurusan"] != "semua")
        or filters.get("tanggal")
        or (filters.get("status") and filters["status"] != "semua")
    )


def user_initials(name: str) -> str:
    parts = name.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper() if name else "??"
