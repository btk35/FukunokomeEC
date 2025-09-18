from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views import View
from .forms import EmailLoginForm
from .forms import SignupForm
from django.contrib.auth import logout


class CustomLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = 'registration/login.html'

class SignupView(View):
    def get(self, request):
        form = SignupForm()
        return render(request, 'registration/signup.html', {'form': form})
    
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'registration/signup.html', {'form': form})

#ログアウト後のリダイレクト先     
def index(request):
    return render(request, 'index.html')

