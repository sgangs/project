from django.shortcuts import render
from django.views.generic import TemplateView

#landing page
class HomeView(TemplateView):
    template_name = "index.html"