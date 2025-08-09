from django.shortcuts import render, redirect
from django.http import HttpResponse
import yt_dlp
import os
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')

        # Har safar yuklashdan oldin .part faylni o‘chirish
        temp_filename = 'video.mp4.part'
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.%(ext)s',
            'noplaylist': True,
            'continuedl': False,  # Resume yo‘q
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)

            # Fayl mavjudligini tekshirish
            if not os.path.exists(filename):
                return render(request, 'home.html', {'error': 'Video yuklab olinmadi.'})

            # Video faylni foydalanuvchiga yuborish
            with open(filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type='video/mp4')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'

            os.remove(filename)  # Foydalanuvchiga yuborgandan keyin o‘chirish
            return response

        except Exception as e:
            return render(request, 'home.html', {'error': f'Xato: {str(e)}'})

    return render(request, 'home.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, reuqest):
        if reuqest.POST.get('password') == reuqest.POST.get('password1'):
            User.objects.create_user(
                username=reuqest.POST.get('username'),
                password=reuqest.POST.get('password')
            )
            return redirect('')
        return redirect('register')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user is not None:
            login(request, user)
            return redirect('video-downloader')
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')