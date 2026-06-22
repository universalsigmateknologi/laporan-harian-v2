from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from laporan.models import FotoBukti, LaporanHarian
from laporan.services.export_excel import generate_excel
from laporan.services.export_pdf import generate_pdf
from laporan.services.rekap import (
    PER_PAGE,
    apply_filters,
    build_page_rows,
    format_tanggal_label,
    get_adjacent_laporan,
    get_base_queryset,
    get_filter_labels,
    get_jurusan_aktif,
    get_rekap_stats,
    get_tahun_ajaran_aktif,
    get_tanggal_options,
    has_active_filters,
    user_initials,
)
from perencanaan.models import Perencanaan
from siswa.models import Siswa
from utils.utils import role_required


def _parse_filters(request):
    return {
        "q": request.GET.get("q", "").strip(),
        "tanggal_dari": request.GET.get("tanggal_dari", "").strip(),
        "tanggal_sampai": request.GET.get("tanggal_sampai", "").strip(),

        "jurusan": request.GET.get("jurusan", "").strip() or "semua",
        "status": request.GET.get("status", "").strip() or "semua",
    }


def _get_filtered_queryset(request):
    tahun_ajaran = get_tahun_ajaran_aktif()
    qs = get_base_queryset(tahun_ajaran)
    filters = _parse_filters(request)
    return apply_filters(
        qs,
        q=filters["q"],
        tanggal_dari=filters["tanggal_dari"],
        tanggal_sampai=filters["tanggal_sampai"],
        jurusan=filters["jurusan"],
        status=filters["status"],
        laporan_id=request.GET.get("laporan_id", "").strip(),
    )


def _get_today_laporan(user):
    if not getattr(user, "is_siswa", False):
        return None
    today = timezone.now().date()
    return LaporanHarian.objects.filter(siswa=user.siswa, tanggal=today).first()


@login_required
@role_required(["siswa"])
def laporan_post(request):
    tahun_ajaran = get_tahun_ajaran_aktif()
    siswa = request.user.siswa
    
    today_laporan = _get_today_laporan(request.user)
    if request.method == "GET" and today_laporan:
        return redirect("laporan:laporan_edit", pk=today_laporan.pk)

    form_data = {
        "uraian_pekerjaan": request.POST.get("uraian_pekerjaan", "") if request.method == "POST" else "",
        "hasil_progress": request.POST.get("hasil_progress", "") if request.method == "POST" else "",
        "status": LaporanHarian.Status.DALAM_PROSES,
    }
    errors = {}

    if request.method == "POST":
        uraian_pekerjaan = request.POST.get("uraian_pekerjaan", "").strip()
        hasil_progress = request.POST.get("hasil_progress", "").strip()
        status = LaporanHarian.Status.DALAM_PROSES
        foto_files = request.FILES.getlist("foto")

        if not uraian_pekerjaan:
            errors["uraian_pekerjaan"] = "Uraian pekerjaan wajib diisi."
        if not hasil_progress:
            errors["hasil_progress"] = "Hasil/progress wajib diisi."
        if not foto_files:
            errors["foto"] = "Minimal satu foto bukti wajib diunggah."
        today = timezone.now().date()
        if siswa and LaporanHarian.objects.filter(siswa=siswa, tanggal=today).exists():
            errors["duplicate"] = "Anda sudah membuat laporan hari ini."

        if not errors:
            laporan = LaporanHarian.objects.create(
                siswa=siswa,
                tahun_ajaran=tahun_ajaran,
                tanggal=today,
                uraian_pekerjaan=uraian_pekerjaan,
                hasil_progress=hasil_progress,
                status=status,
            )
            for foto in foto_files:
                FotoBukti.objects.create(laporan=laporan, foto=foto)

            messages.success(request, "Laporan berhasil dikirim.")
            return redirect("laporan:rekap_harian")

        form_data.update({
            "uraian_pekerjaan": uraian_pekerjaan,
            "hasil_progress": hasil_progress,
            "status": status,
        })

    perencanaan_list = Perencanaan.objects.filter(siswa=siswa).select_related("program")

    context = {
        "page_title": "Buat Laporan Baru",
        "active_menu": "rekap_harian",
        "siswa": siswa,
        "tahun_ajaran": tahun_ajaran,
        "form_data": form_data,
        "errors": errors,
        "status_choices": LaporanHarian.Status.choices,
        "form_action": reverse("laporan:laporan_post"),
        "submit_label": "Kirim Laporan",
        "is_edit": False,
        "perencanaan_list": perencanaan_list,
    }
    return render(request, "laporan/laporan_post.html", context)


@login_required
@role_required(["siswa"])
def laporan_edit(request, pk):
    siswa = request.user.siswa
    laporan = get_object_or_404(LaporanHarian, pk=pk, siswa=siswa)
    tahun_ajaran = laporan.tahun_ajaran
    form_data = {
        "uraian_pekerjaan": request.POST.get("uraian_pekerjaan", laporan.uraian_pekerjaan) if request.method == "POST" else laporan.uraian_pekerjaan,
        "hasil_progress": request.POST.get("hasil_progress", laporan.hasil_progress) if request.method == "POST" else laporan.hasil_progress,
        "status": request.POST.get("status", laporan.status) if request.method == "POST" else laporan.status,
    }
    errors = {}

    if request.method == "POST":
        uraian_pekerjaan = request.POST.get("uraian_pekerjaan", "").strip()
        hasil_progress = request.POST.get("hasil_progress", "").strip()
        status = request.POST.get("status", laporan.status)
        foto_files = request.FILES.getlist("foto")

        if not uraian_pekerjaan:
            errors["uraian_pekerjaan"] = "Uraian pekerjaan wajib diisi."
        if not hasil_progress:
            errors["hasil_progress"] = "Hasil/progress wajib diisi."
        status = LaporanHarian.Status.DALAM_PROSES
        if not laporan.foto_bukti.exists() and not foto_files:
            errors["foto"] = "Minimal satu foto bukti wajib diunggah."

        if not errors:
            laporan.uraian_pekerjaan = uraian_pekerjaan
            laporan.hasil_progress = hasil_progress
            laporan.status = status
            laporan.save(update_fields=["uraian_pekerjaan", "hasil_progress", "status", "updated_at"])
            for foto in foto_files:
                FotoBukti.objects.create(laporan=laporan, foto=foto)

            messages.success(request, "Laporan berhasil diperbarui.")
            return redirect("laporan:rekap_harian")

        form_data.update({
            "uraian_pekerjaan": uraian_pekerjaan,
            "hasil_progress": hasil_progress,
            "status": status,
        })

    perencanaan_list = Perencanaan.objects.filter(siswa=laporan.siswa).select_related("program")

    context = {
        "page_title": "Edit Laporan",
        "active_menu": "rekap_harian",
        "siswa": laporan.siswa,
        "tahun_ajaran": tahun_ajaran,
        "laporan": laporan,
        "form_data": form_data,
        "errors": errors,
        "status_choices": LaporanHarian.Status.choices,
        "form_action": reverse("laporan:laporan_edit", args=[laporan.pk]),
        "submit_label": "Simpan Perubahan",
        "is_edit": True,
        "perencanaan_list": perencanaan_list,
    }
    return render(request, "laporan/laporan_post.html", context)


@login_required
def rekap_harian(request):
    tahun_ajaran = get_tahun_ajaran_aktif()
    base_qs = get_base_queryset(tahun_ajaran)
    filters = _parse_filters(request)
    filtered_qs = apply_filters(
        base_qs,
        q=filters["q"],
        tanggal_dari=filters["tanggal_dari"],
        tanggal_sampai=filters["tanggal_sampai"],
        jurusan=filters["jurusan"],
        status=filters["status"],
    )

    paginator = Paginator(filtered_qs, PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    jurusan_list = get_jurusan_aktif()
    tanggal_options = get_tanggal_options(base_qs)
    stats = get_rekap_stats(base_qs)
    filter_labels = get_filter_labels(filters)


    jurusan_label = "Semua Jurusan"
    if filters["jurusan"] and filters["jurusan"] != "semua":
        jurusan_label = filters["jurusan"].upper()

    tanggal_label = "Semua Tanggal"
    if filters.get("tanggal_dari") and filters.get("tanggal_sampai"):
        tanggal_label = f"{filters['tanggal_dari']} s/d {filters['tanggal_sampai']}"
    elif filters.get("tanggal_dari"):
        tanggal_label = f"Dari {filters['tanggal_dari']}"
    elif filters.get("tanggal_sampai"):
        tanggal_label = f"Sampai {filters['tanggal_sampai']}"


    display_name = request.user.get_full_name() or request.user.username

    context = {
        "page_title": "Rekap Harian Kegiatan",
        "active_menu": "rekap_harian",
        "tahun_ajaran": tahun_ajaran,
        "jurusan_list": jurusan_list,
        "tanggal_options": tanggal_options,
        "stats": stats,
        "filters": filters,
        "filter_labels": filter_labels,
        "has_active_filters": has_active_filters(filters),
        "jurusan_label": jurusan_label,
        "tanggal_label": tanggal_label,
        "page_obj": page_obj,
        "laporan_rows": build_page_rows(page_obj.object_list),
        "filtered_count": paginator.count,
        "per_page": PER_PAGE,
        "user_display": display_name,
        "user_email": request.user.email or "",
        "user_initials": user_initials(display_name),
        "is_siswa": request.user.is_siswa,
        "is_admin": request.user.is_admin,
        "today_laporan": _get_today_laporan(request.user),
        "export_query": request.GET.urlencode(),
        "format_tanggal_label": format_tanggal_label,
    }
    return render(request, "laporan/laporan.html", context)


def _rekap_list_query(request):
    """Query string untuk kembali ke daftar rekap (tanpa parameter halaman)."""
    q = request.GET.copy()
    q.pop("page", None)
    return q.urlencode()


def _detail_nav_query(request, _pk=None):
    """Query string untuk navigasi prev/next sambil mempertahankan filter rekap."""
    q = request.GET.copy()
    q.pop("page", None)
    return q.urlencode()


@login_required
def laporan_detail(request, pk):
    tahun_ajaran = get_tahun_ajaran_aktif()
    base_qs = get_base_queryset(tahun_ajaran)
    laporan = get_object_or_404(
        base_qs.select_related("siswa", "siswa__jurusan", "siswa__pembimbing"),
        pk=pk,
    )
    fotos = list(laporan.foto_bukti.all())

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "verifikasi":
            laporan.status = LaporanHarian.Status.SELESAI
            laporan.save(update_fields=["status", "updated_at"])
            messages.success(request, "Laporan ditandai selesai.")
        elif action == "revisi":
            laporan.status = LaporanHarian.Status.DALAM_PROSES
            laporan.save(update_fields=["status", "updated_at"])
            messages.info(request, "Laporan dikembalikan ke status dalam proses.")
        nav_qs = _detail_nav_query(request)
        url = reverse("laporan:detail", args=[pk])
        if nav_qs:
            url = f"{url}?{nav_qs}"
        return redirect(url)

    filters = _parse_filters(request)
    filtered_qs = apply_filters(
        base_qs,
        q=filters["q"],
        tanggal_dari=filters["tanggal_dari"],
        tanggal_sampai=filters["tanggal_sampai"],
        jurusan=filters["jurusan"],
        status=filters["status"],
    )
    prev_laporan, next_laporan = get_adjacent_laporan(filtered_qs, pk)

    rekap_query = _rekap_list_query(request)
    back_url = reverse("laporan:rekap_harian")
    if rekap_query:
        back_url = f"{back_url}?{rekap_query}"

    nav_qs = _detail_nav_query(request)
    export_query = f"laporan_id={pk}"
    foto_urls = [f.foto.url for f in fotos if f.foto]

    display_name = request.user.get_full_name() or request.user.username
    # `LaporanHarian` doesn't have `tanggal`; use `created_at.date()` instead
    tanggal_label = format_tanggal_label(laporan.created_at.date())

    context = {
        "page_title": "Detail Laporan",
        "active_menu": "rekap_harian",
        "laporan": laporan,
        "fotos": fotos,
        "foto_urls": foto_urls,
        "tanggal_label": tanggal_label,
        "back_url": back_url,
        "nav_qs": nav_qs,
        "prev_laporan": prev_laporan,
        "next_laporan": next_laporan,
        "export_query": export_query,
        "user_display": display_name,
        "user_email": request.user.email or "",
        "user_initials": user_initials(display_name),
    }
    return render(request, "laporan/laporan_detail.html", context)


@login_required
def export_pdf(request):
    queryset = _get_filtered_queryset(request)
    tahun_ajaran = get_tahun_ajaran_aktif()
    pdf_bytes = generate_pdf(
        queryset,
        base_url=request.build_absolute_uri("/"),
        tahun_ajaran_nama=tahun_ajaran.nama if tahun_ajaran else "",
    )

    filename = f"rekap_harian_{timezone.now():%Y%m%d_%H%M}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_excel(request):
    queryset = _get_filtered_queryset(request)
    buffer = generate_excel(queryset)

    filename = f"rekap_harian_{timezone.now():%Y%m%d_%H%M}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
