"""distributor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from distributor import views

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.HomeView.as_view()),
    url(r'^register/$', views.RegisterView, name='register'),
    url(r'^login/', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^master/', include('distribution_master.urls',namespace='master', app_name='master')),
    url(r'^purchase/', include('distribution_purchase.urls',namespace='purchase', app_name='purchase')),
    url(r'^sales/', include('distribution_sales.urls',namespace='sales', app_name='sales')),
    url(r'^inventory/', include('distribution_inventory.urls',namespace='inventory', app_name='inventory')),
    url(r'^accounts/', include('distribution_accounts.urls',namespace='accounts', app_name='accounts')),
]