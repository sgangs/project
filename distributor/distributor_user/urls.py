from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^tenantsettings/data/$', views.tenant_settings_data, name='tenant_settings_data'),
    url(r'^tenantsettings/$', views.tenant_settings, name='tenant_settings'),
    url(r'^userlist/$', views.user_list, name='user_list'),
    url(r'^userlist/data/$', views.user_list_data, name='user_list_data'),
    # url(r'^balancesheet/$', views.balance_sheet, name='balance_sheet'),
    # url(r'^invoice/api/getproduct$', views.get_product, name='get_product'),
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
]