from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, password_reset_confirm,\
        password_reset_complete, password_change, password_change_done

# from rest_framework.authtoken import views as drfviews
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from distributor import views
from .forms import revisedPasswordResetForm

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.HomeView.as_view()),
    url(r'^register/$', views.RegisterView, name='register'),
    # url(r'^registration-success/$', views.Registration),

    #Login and logout
    url(r'^login/', views.custom_login, name='login'),
    url(r'^logout/$', logout, name='logout'),

    #change password
    url(r'^password-change/$',password_change,name='password_change'),
    url(r'^password-change/done/$',password_change_done,name='password_change_done'),

    # restore password urls
    url(r'^password-reset/$', views.custom_password_reset, {'from_email': 'support@techassisto.com', \
        'subject_template_name':"Assisto-Your Technical Assistant Reset Password",\
        'password_reset_form':revisedPasswordResetForm},name='password_reset'),
    url(r'^password-reset/done/$', password_reset_done, name='password_reset_done'),
    url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', password_reset_confirm, name='password_reset_confirm'),
    url(r'^password-reset/complete/$', password_reset_complete, name='password_reset_complete'),

    #Get & refresh token - tried to make this url difficult to guess but easy to understand
    # url(r'^getthetoken/', drfviews.obtain_auth_token),
    url(r'^getthetoken/', obtain_jwt_token), 
    url(r'^refreshthetoken/', refresh_jwt_token),

    url(r'^landing/$', views.landing, name='landing'),
    url(r'^tenant-user-metadata/$', views.tenant_user_metadata, name='tenant_user_metadata'),

    url(r'^master/', include('distributor_master.urls',namespace='master', app_name='master')),
    url(r'^user/', include('distributor_user.urls',namespace='user', app_name='user')),
    url(r'^purchase/', include('distributor_purchase.urls',namespace='purchase', app_name='purchase')),
    url(r'^sales/', include('distributor_sales.urls',namespace='sales', app_name='sales')),
    url(r'^retailsales/', include('retail_sales.urls',namespace='retailsales', app_name='retailsales')),
    url(r'^account/', include('distributor_account.urls',namespace='account', app_name='account')),
    url(r'^inventory/', include('distributor_inventory.urls',namespace='inventory', app_name='inventory')),
    url(r'^payment/', include('payumoney.urls',namespace='payumoney', app_name='payumoney')),
    
    # url(r'^inventory/', include('distribution_inventory.urls',namespace='inventory', app_name='inventory')),
    # url(r'^accounts/', include('distribution_accounts.urls',namespace='accounts', app_name='accounts')),
    # url(r'^hr/', include('distribution_hr.urls',namespace='hr', app_name='hr')),

    # url(r'^payment/', include('payumoney.urls',namespace='payumoney', app_name='payumoney')),
]