from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    # url(r'^zone/getdata/$', views.zone_view, name='zone_view'),
    url(r'^invoice/api/getproduct$', views.get_product, name='get_product'),
    url(r'^invoice/api/getproductrate$', views.get_product_inventory, name='getinvoice'),
    url(r'^invoice/save/$', views.sales_invoice_save, name='sales_invoice_save'),
    # url(r'^invoice/detailview/(?P<pk>[-\S]+)/$$', views.invoice_detail_view, name='invoice_detail_view'),
    # url(r'^invoice/detail/(?P<pk>[-\S]+)/$', views.invoice_details, name='invoice_details'),
    # url(r'^invoicelist/$', views.invoice_list, name='invoice_list'),
    # url(r'^invoicelist/listall/$', views.all_invoices, name='all_invoices'),
    # url(r'^invoicelist/metadata/$', views.invoices_metadata, name='invoices_metadata'),
    url(r'^invoice/$', views.new_sales_invoice, name='new_sales_invoice'),
    # url(r'^invoice/paymentsave/$', views.payment_register, name='payment_register'),
    # url(r'^salestotalvalue/$', views.sales_total_values, name='sales_total_values'),
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),    
]