from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from utils import utils

# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect(utils.get_redirect_url_by_role(request.user))

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Username dan kata sandi wajib diisi.')
            return render(request, 'accounts/auth/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Selamat datang kembali, {user.get_full_name() or user.username}!')
                return redirect(utils.get_redirect_url_by_role(user))
            else:
                messages.error(request, 'Akun Anda telah dinonaktifkan. Silakan hubungi admin.')
        else:
            messages.error(request, 'Username atau kata sandi salah.')

    return render(request, 'accounts/auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')