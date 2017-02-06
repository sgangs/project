from django.shortcuts import render
from django.views.generic import TemplateView

#landing page
class HomeView(TemplateView):
    template_name = "index.html"

#400 error
def bad_request(request):
    return render (request, 'error/400.html')

#403 error
def permission_denied(request):
    return render (request, 'error/403.html')

#404 error
def page_not_found(request):
    return render (request, 'error/404.html')

#500 error
def server_error(request):
    return render (request, 'error/500.html')