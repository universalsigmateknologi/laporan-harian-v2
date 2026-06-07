from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from utils import utils

# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect(utils.get_redirect_url_by_role(request.user))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        login(request, user)
        return redirect('/laporan/rekap/')

    return render(request, 'accounts/auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')