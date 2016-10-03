from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^invoice/$', views.salesinvoice, {'type': 'Sales Invoice'}, name='invoice_new'),
    url(r'^invoicebase/$', views.sales_base, name='base'),
    url(r'^invoicelist/$', views.sales_list, {'type': 'List'}, name='invoice_list'),
    url(r'^invoicedue/$', views.sales_due, {'type': 'Due'}, name='invoice_due'),
    url(r'^customerdue/$', views.customer_due, {'type': 'Due List'}, name='customer_due'),
    url(r'^(?P<detail>[-\S]+)/due/$',views.sales_detail, {'type': 'Due'}, name='invoice_detail_due'),
    url(r'^(?P<detail>[-\S]+)/$',views.sales_detail, {'type': 'Detail'}, name='invoice_detail'),    
]
