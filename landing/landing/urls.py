from django.conf.urls import url
from django.contrib import admin

from landing_base import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.HomeView.as_view()),
]
