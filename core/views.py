from django.shortcuts import render
from django.contrib.auth.views import LoginView

def home(request):
    return render(request, 'core/home.html')

class TeamLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ورود به پنل تیم'
        return context
