from django.shortcuts import render
from django.views.generic import TemplateView

class LoginGuideView(TemplateView):
    template_name = 'security/login_guide.html'