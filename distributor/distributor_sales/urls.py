from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    # url(r'^zone/getdata/$', views.zone_view, name='zone_view'),
    url(r'^invoice/api/getproduct$', views.get_product, name='get_product'),
    url(r'^invoice/api/getproductwarehouse$', views.get_product_inventory, name='getinvoice'),
    url(r'^invoice/save/$', views.sales_invoice_save, name='sales_invoice_save'),
    url(r'^invoice/detailview/(?P<pk>[-\S]+)/$$', views.invoice_detail_view, name='invoice_detail_view'),
    url(r'^invoice/detail/(?P<pk>[-\S]+)/$', views.invoice_details, name='invoice_details'),
    url(r'^invoice/excel/(?P<pk>[-\S]+)/$', views.excel_invoice, name='excel_invoice'),
    url(r'^invoicelist/$', views.invoice_list, name='invoice_list'),
    url(r'^invoicelist/listall/$', views.all_invoices, name='all_invoices'),

    url(r'^invoicelist/purchasedetails/$', views.invoice_purchase_wise_details, name='invoice_purchase_wise_details'),
    
    url(r'^invoice/salesedit/$', views.sales_edit_view, name='sales_edit_view'),
    url(r'^invoice/salesedit/data/$', views.edit_invoice_details, name='edit_invoice_details'),
    url(r'^invoice/salesedit/save/$', views.sales_invoice_edit, name='sales_invoice_edit'),
    
    url(r'^invoice/openinvoice/listall/$', views.open_invoice_list, name='open_invoice_list'),
    url(r'^invoice/openinvoice/save/$', views.finalize_open_invoices, name='finalize_open_invoices'),
    url(r'^invoice/openinvoice/$', views.open_invoices, name='open_invoices'),
    
    url(r'^invoicelist/metadata/$', views.invoices_metadata, name='invoices_metadata'),
    url(r'^invoice/$', views.new_sales_invoice, name='new_sales_invoice'),
    url(r'^invoice/paymentsave/$', views.payment_register, name='payment_register'),
    url(r'^salestotalvalue/$', views.sales_total_values, name='sales_total_values'),
    
    url(r'^collectionlist/$', views.collection_list, name='collection_list'),
    url(r'^collectionlistview/$', views.collection_list_view, name='collection_list_view'),
    url(r'^invoice/customerpending/$', views.get_customer_pending, name='get_customer_pending'),
    
    url(r'^invoice/salesreturn/data/$', views.get_return_data, name='get_return_data'),
    url(r'^invoice/salesreturn/$', views.sales_return_view, name='sales_return_view'),
    url(r'^invoice/salesreturn/save/$', views.sales_return_save, name='sales_return_save'),
    url(r'^salesreturn/$', views.return_list_view, name='return_list_view'),
    url(r'^salesreturn/listall/$', views.all_return, name='all_return'),
    
    url(r'^salesreport/$', views.sales_report, name='sales_report'),
    url(r'^salesreport/data/$', views.sales_report_data, name='sales_report_data'),
    
    url(r'^salesreport/customerwise/$', views.customer_wise_sales, name='customer_wise_sales'),
    url(r'^salesreport/customerwise/data/$', views.customer_wise_sales_data, name='customer_wise_sales_data'),

    url(r'^salesreport/customerwisesummary/data/$', views.get_customer_wise_summary, name='get_customer_wise_summary'),

    url(r'^hsnreport/$', views.hsn_report, name='hsn_report'),
    url(r'^hsnreport/data/$', views.get_hsn_report, name='get_hsn_report'),
    
    url(r'^customer-summary/$', views.customer_wise_summary, name='customer_wise_summary'),
    url(r'^customer-summary/data/$', views.get_customer_wise_summary, name='get_customer_wise_summary'),
    # url(r'^customer-detail/pdf/$', views.customer_data_pdf, name='customer_data_pdf'),
]