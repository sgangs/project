from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    #url(r'^base/$', views.base, name='base'),
    url(r'^monthlyfeestructure/$', views.feestructure_new, {'input_type': 'Monthly Fees'}, name='new_monthly_fee'),
    url(r'^yearlyfeestructure/$', views.feestructure_new, {'input_type': 'Yearly Fees'}, name='new_yearly_fee'),
    url(r'^groupfeelinking/$', views.group_fee_linking,  name='group_fee_linking'),
    url(r'^monthlyfeeview/$', views.fee_view, {'input_type': 'Monthly Fees'}, name='monthly_fee_view'),
    url(r'^yearlyfeeview/$', views.fee_view,  {'input_type': 'Yearly Fees'}, name='yearly_fee_view'),
    #url(r'^(?P<detail>[-\S]+)/$',views.purchase_detail, {'type': 'Detail'}, name='invoice_detail'),
]

