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
    url(r'^hr/', include('distribution_hr.urls',namespace='hr', app_name='hr')),
]