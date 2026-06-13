from datetime import date
from django.db.models import Q, QuerySet
from .models import Perencanaan, KategoriPerencanaan
from master.models import Jurusan

PER_PAGE = 20

def get_jurusan_aktif():
    return Jurusan.objects.filter(is_active=True).order_by("kode")

def get_base_queryset() -> QuerySet:
    return Perencanaan.objects.select_related("siswa", "siswa__jurusan", "kategori", "client").all()

def apply_filters(
    queryset: QuerySet,
    *,
    q: str = "",
    start_date: str = "",
    end_date: str = "",
    jurusan: str = "",
    order: str = "desc",
) -> QuerySet:
    if q:
        queryset = queryset.filter(
            Q(siswa__nama_lengkap__icontains=q) | 
            Q(program__icontains=q) |
            Q(kegiatan__icontains=q) |
            Q(client__name__icontains=q)
        )
    
    if start_date:
        try:
            queryset = queryset.filter(waktu__gte=date.fromisoformat(start_date))
        except ValueError:
            pass
            
    if end_date:
        try:
            queryset = queryset.filter(waktu__lte=date.fromisoformat(end_date))
        except ValueError:
            pass
            
    if jurusan and jurusan != "semua":
        queryset = queryset.filter(siswa__jurusan__kode__iexact=jurusan)
        
    if order == "asc":
        queryset = queryset.order_by("waktu", "created_at")
    else:
        queryset = queryset.order_by("-waktu", "-created_at")
        
    return queryset

def get_perencanaan_stats(queryset: QuerySet) -> dict:
    total = queryset.count()
    jumlah_siswa = queryset.values("siswa").distinct().count()
    jumlah_client = queryset.values("client").distinct().count()
    return {
        "total": total,
        "jumlah_siswa": jumlah_siswa,
        "jumlah_client": jumlah_client,
    }

def get_filter_labels(filters: dict) -> dict:
    labels = {}
    if filters.get("jurusan") and filters["jurusan"] != "semua":
        labels["jurusan"] = filters["jurusan"].upper()
    if filters.get("start_date"):
        labels["start_date"] = filters["start_date"]
    if filters.get("end_date"):
        labels["end_date"] = filters["end_date"]
    if filters.get("q"):
        labels["q"] = filters["q"]
    return labels

def has_active_filters(filters: dict) -> bool:
    return bool(
        filters.get("q")
        or (filters.get("jurusan") and filters["jurusan"] != "semua")
        or filters.get("start_date")
        or filters.get("end_date")
    )
