from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # Bisa dilempar ke halaman 403 atau di-redirect ke home
                return redirect('home') 
        return wrap
    return decorator


def get_redirect_url_by_role(user):
    """
    Fungsi untuk menentukan URL redirect berdasarkan role user.
    """        
    # Deteksi role user
    if user.role == 'admin':
        return '/laporan/rekap/'
    elif user.role == 'pembimbing':
        return '/laporan/rekap/'
    elif user.role == 'siswa':
        return '/laporan/rekap/'
        
    # URL default jika role tidak dikenali
    return 'home'