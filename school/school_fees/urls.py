from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^base/$', views.base, name='base'),
    url(r'^monthlyfeestructure/$', views.feestructure_new,  {'input_type': 'Monthly Fees'}, name='new_monthly_fee'),
    url(r'^yearlyfeestructure/$', views.feestructure_new, {'input_type': 'Yearly Fees'}, name='new_yearly_fee'),
    url(r'^groupfeelinking/$', views.group_fee_linking,  name='group_fee_linking'),
    url(r'^monthlyfeeview/$', views.fee_view, {'input_type': 'Monthly Fees'}, name='monthly_fee_view'),
    url(r'^yearlyfeeview/$', views.fee_view,  {'input_type': 'Yearly Fees'}, name='yearly_fee_view'),
    url(r'^studentfeepayment/$', views.student_payment, {'input_type': 'Payment'}, name='student_payment'),
    url(r'^feecollection/$', views.fee_collected_between, name='fee_collection'),
    url(r'^studentwisehistory/$', views.fee_payment_history, name='studentwise_history'),
    url(r'^feepaymentmonthwise/$', views.fee_payment_monthwise, name='fee_payment_monthwise'),
    url(r'^feeslicingdicing/$', views.fee_collection_graph, name='fee_report'),
    url(r'^studentfeepaymentview/$', views.student_payment, {'input_type': 'View'}, name='student_payment_view'),
    # url(r'^printfee/$', views.print_fee_structure, name='student_fee_print'),
    #url(r'^(?P<detail>[-\S]+)/$',views.purchase_detail, {'type': 'Detail'}, name='invoice_detail'),
]

