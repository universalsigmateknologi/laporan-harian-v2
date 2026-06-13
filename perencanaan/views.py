from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Perencanaan, Client, KategoriPerencanaan
from .forms import PerencanaanForm
from .services import (
    get_base_queryset, apply_filters, get_perencanaan_stats, 
    get_jurusan_aktif, get_filter_labels, has_active_filters, PER_PAGE
)
from utils.utils import role_required

def _parse_filters(request):
    return {
        "q": request.GET.get("q", "").strip(),
        "start_date": request.GET.get("start_date", "").strip(),
        "end_date": request.GET.get("end_date", "").strip(),
        "jurusan": request.GET.get("jurusan", "").strip() or "semua",
        "order": request.GET.get("order", "desc").strip(),
    }

@login_required
def perencanaan_list(request):
    filters = _parse_filters(request)
    base_qs = get_base_queryset()
    filtered_qs = apply_filters(
        base_qs,
        q=filters["q"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        jurusan=filters["jurusan"],
        order=filters["order"]
    )

    paginator = Paginator(filtered_qs, PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    stats = get_perencanaan_stats(base_qs)
    jurusan_list = get_jurusan_aktif()
    filter_labels = get_filter_labels(filters)

    is_siswa = request.user.role == 'siswa'
    is_admin = request.user.role == 'admin'
    can_edit = is_siswa or is_admin

    context = {
        "page_title": "Daftar Perencanaan",
        "active_menu": "perencanaan",
        "page_obj": page_obj,
        "stats": stats,
        "filters": filters,
        "filter_labels": filter_labels,
        "has_active_filters": has_active_filters(filters),
        "jurusan_list": jurusan_list,
        "can_edit": can_edit,
        "is_siswa": is_siswa,
        "is_admin": is_admin,
    }
    return render(request, "perencanaan/perencanaan_list.html", context)

@login_required
def perencanaan_create(request):
    if request.user.role not in ['siswa', 'admin']:
        messages.error(request, "Anda tidak memiliki akses untuk menambah perencanaan.")
        return redirect("perencanaan:list")
    
    show_siswa = request.user.role == 'admin'
    
    if request.method == "POST":
        form = PerencanaanForm(request.POST, show_siswa=show_siswa)
        if form.is_valid():
            perencanaan = form.save(commit=False)
            if request.user.role == 'siswa':
                perencanaan.siswa = request.user.siswa
            perencanaan.save()
            messages.success(request, "Perencanaan berhasil ditambahkan.")
            return redirect("perencanaan:list")
    else:
        form = PerencanaanForm(show_siswa=show_siswa)
    
    context = {
        "page_title": "Tambah Perencanaan",
        "active_menu": "perencanaan",
        "form": form,
    }
    return render(request, "perencanaan/perencanaan_form.html", context)

@login_required
def perencanaan_update(request, pk):
    perencanaan = get_object_or_404(Perencanaan, pk=pk)
    
    # Permission check
    if request.user.role == 'siswa' and perencanaan.siswa.user != request.user:
        messages.error(request, "Anda hanya dapat mengubah perencanaan milik sendiri.")
        return redirect("perencanaan:list")
    if request.user.role not in ['siswa', 'admin']:
        messages.error(request, "Anda tidak memiliki akses untuk mengubah perencanaan.")
        return redirect("perencanaan:list")

    show_siswa = request.user.role == 'admin'

    if request.method == "POST":
        form = PerencanaanForm(request.POST, instance=perencanaan, show_siswa=show_siswa)
        if form.is_valid():
            form.save()
            messages.success(request, "Perencanaan berhasil diperbarui.")
            return redirect("perencanaan:list")
    else:
        form = PerencanaanForm(instance=perencanaan, show_siswa=show_siswa)
    
    context = {
        "page_title": "Edit Perencanaan",
        "active_menu": "perencanaan",
        "form": form,
        "perencanaan": perencanaan,
    }
    return render(request, "perencanaan/perencanaan_form.html", context)

@login_required
def perencanaan_delete(request, pk):
    perencanaan = get_object_or_404(Perencanaan, pk=pk)
    
    # Permission check
    if request.user.role == 'siswa' and perencanaan.siswa.user != request.user:
        messages.error(request, "Anda hanya dapat menghapus perencanaan milik sendiri.")
        return redirect("perencanaan:list")
    if request.user.role not in ['siswa', 'admin']:
        messages.error(request, "Anda tidak memiliki akses untuk menghapus perencanaan.")
        return redirect("perencanaan:list")

    if request.method == "POST":
        perencanaan.delete()
        messages.success(request, "Perencanaan berhasil dihapus.")
        return redirect("perencanaan:list")
    
    return render(request, "perencanaan/perencanaan_confirm_delete.html", {"perencanaan": perencanaan})
