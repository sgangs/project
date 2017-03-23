from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    url(r'^base/$', views.base, name='base'),
    url(r'^genericfeestructure/$', views.feestructure_new,  {'input_type': 'Monthly Fees'}, name='new_generic_fee'),
    url(r'^groupfeelinking/$', views.group_fee_linking,  name='group_fee_linking'),
    url(r'^genericfeeview/$', views.fee_view,  {'input_type': 'Generic Fees'}, name='generic_fee_view'),
    url(r'^studentfeepayment/$', views.student_payment, {'input_type': 'Payment'}, name='student_payment'),
    url(r'^feecollection/$', views.fee_collected_between, name='fee_collection'),
    url(r'^studentwisehistory/$', views.fee_payment_history, name='studentwise_history'),
    url(r'^feepaymentmonthwise/$', views.fee_payment_monthwise, name='fee_payment_monthwise'),
    url(r'^studentfeeedit/$', views.student_fee_structure, name='student_fee_structure'),
    url(r'^feeslicingdicing/$', views.fee_collection_graph, name='fee_report'),
    url(r'^studentfeepaymentview/$', views.student_payment, {'input_type': 'View'}, name='student_payment_view'),
    # url(r'^printfee/$', views.print_fee_structure, name='student_fee_print'),
    #url(r'^(?P<detail>[-\S]+)/$',views.purchase_detail, {'type': 'Detail'}, name='invoice_detail'),
]

