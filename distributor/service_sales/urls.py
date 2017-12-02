from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    # url(r'^zone/getdata/$', views.zone_view, name='zone_view'),
    url(r'^invoice/api/getproduct$', views.get_product, name='get_product'),
    # url(r'^invoice/api/getproductbarcode$', views.get_product_barcode, name='get_product_barcode'),
    url(r'^invoice/api/getproductrate$', views.get_product_rate, name='getinvoice'),
    # url(r'^invoice/api/getproduct/details$', views.get_product_data, name='get_product_data'),
    url(r'^getsalesusers/$', views.service_sales_user, name='service_sales_user'),

    url(r'^invoice/$', views.new_sales_invoice, name='new_sales_invoice'),
    url(r'^invoice/save/$', views.sales_invoice_save, name='sales_invoice_save'),
    
    url(r'^invoice/productdetailview/(?P<pk>[-\S]+)/$$', views.invoice_product_detail_view, name='invoice_product_detail_view'),
    url(r'^invoice/productdetail/(?P<pk>[-\S]+)/$', views.invoice_product_details, name='invoice_product_details'),

    url(r'^invoice/servicedetailview/(?P<pk>[-\S]+)/$$', views.invoice_service_detail_view, name='invoice_service_detail_view'),
    url(r'^invoice/servicedetail/(?P<pk>[-\S]+)/$', views.invoice_service_details, name='invoice_service_details'),

    url(r'^invoicelist/$', views.invoice_list, name='invoice_list'),
    url(r'^invoicelist/listall/$', views.all_invoices, name='all_invoices'),

    url(r'^user-wise-service/$', views.user_service_view, name='user_service_view'),
    url(r'^user-wise-service/data/$', views.user_service_data, name='user_service_data'),

    # User wise report: User wise sales (daily/monthly). Sales by User-Service Group wise. Sale user-wise 
        
]