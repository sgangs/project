from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    # url(r'^zone/getdata/$', views.zone_view, name='zone_view'),
    url(r'^invoice/api/getproduct$', views.get_product, name='get_product'),
    url(r'^invoice/api/getproductbarcode$', views.get_product_barcode, name='get_product_barcode'),
    url(r'^invoice/api/getproductrate$', views.get_product_inventory, name='getinvoice'),
    url(r'^invoice/api/getproduct/details$', views.get_product_data, name='get_product_data'),

    url(r'^invoice/$', views.new_sales_invoice, name='new_sales_invoice'),    
    url(r'^invoice/save/$', views.sales_invoice_save, name='sales_invoice_save'),
    
    url(r'^invoice/detailview/(?P<pk>[-\S]+)/$$', views.invoice_detail_view, name='invoice_detail_view'),
    url(r'^invoice/detail/(?P<pk>[-\S]+)/$', views.invoice_details, name='invoice_details'),
    url(r'^invoice/invoicenodetails/$', views.invoice_details_with_no, name='invoice_details_with_no'),

    url(r'^invoiceedit/$', views.sales_invoice_edit_view, name='sales_invoice_edit_view'),
    url(r'^invoiceedit/save/$', views.sales_invoice_edit, name='sales_invoice_edit'),
    
    url(r'^invoicelist/$', views.invoice_list, name='invoice_list'),
    url(r'^invoicelist/listall/$', views.all_invoices, name='all_invoices'),
    url(r'^invoicelist/listall/app/$', views.all_invoice_app, name='all_invoice_app'),

    url(r'^invoice/purchasedetails/$', views.invoice_purchase_wise_details, name='invoice_purchase_wise_details'),

    # url(r'^invoicelist/metadata/$', views.invoices_metadata, name='invoices_metadata'),
    
    url(r'^invoice/delete/$', views.sales_invoice_delete, name='sales_invoice_delete'),

    url(r'^paymentmode/$', views.get_payment_mode, name='get_payment_mode'),

    url(r'^invoice/salesreturn$', views.sales_return_view, name='sales_return_view'),
    url(r'^invoice/salesreturn/data/$', views.get_return_data, name='get_return_data'),
    url(r'^invoice/salesreturn/save/$', views.sales_return_save, name='sales_return_save'),
    url(r'^eodsales/data/$', views.eod_sales_data, name='eod_sales_data'),
    url(r'^eodsales/$', views.eod_sales_report, name='eod_sales_report'),
    url(r'^salessummarygraph/$', views.sales_summary_graph, name='sales_last_three_days'),
    # url(r'^invoice/paymentsave/$', views.payment_register, name='payment_register'),
    # url(r'^salestotalvalue/$', views.sales_total_values, name='sales_total_values'),
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),  

    url(r'^retail-dashboard/$', views.retail_dashboard, name='retail_dashboard'),
    url(r'^retail-dashboard/data/$', views.retail_dashboard_data, name='retail_dashboard_data'),
]