from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    # url(r'^zone/getdata/$', views.zone_view, name='zone_view'),
    url(r'^receipt/$', views.purchase_receipt_new, name='purchase_receipt_new'),
    url(r'^receipt/save/$', views.purchase_receipt_save, name='purchase_receipt_save'),
    url(r'^receipt/detailview/(?P<pk>[-\S]+)/$$', views.receipts_detail_view, name='receipts_detail_view'),
    url(r'^receipt/api/getproduct$', views.get_product, name='get_product'),
    url(r'^receipt/detail/(?P<pk>[-\S]+)/$', views.receipts_details, name='receipts_details'),
    url(r'^receipt/excel/(?P<pk>[-\S]+)/$$', views.excel_receipt, name='excel_receipt'),
    url(r'^receiptlist/listall/$', views.all_receipts, name='all_receipts'),
    url(r'^receiptlist/metadata/$', views.receipts_metadata, name='receipts_metadata'),
    url(r'^receipt/paymentsave/$', views.payment_register, name='payment_register'),
    url(r'^paymentlist/$', views.payment_list, name='payment_list'),
    url(r'^paymentlistview/$', views.payment_list_view, name='payment_list_view'),
    url(r'^receiptlist/$', views.receipt_list, name='receipt_list'),
    url(r'^debitnotereturn/$', views.debit_note_return_view, name='debit_note_return_view'),
    url(r'^productinventorydetails/$', views.product_inventory_details, name='product_inventory_details'),
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),    
]