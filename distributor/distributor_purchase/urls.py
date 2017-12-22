from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^receipt-order/(?P<pk>[-\S]+)/$', views.receipt_order, name='receipt_order'),

    url(r'^receipt/$', views.purchase_receipt_new, name='purchase_receipt_new'),
    url(r'^receipt/save/$', views.purchase_receipt_save, name='purchase_receipt_save'),
    url(r'^receipt/detailview/(?P<pk>[-\S]+)/$', views.receipts_detail_view, name='receipts_detail_view'),
    url(r'^receipt/api/getproduct$', views.get_product, name='get_product'),
    url(r'^receipt/detail/(?P<pk>[-\S]+)/$', views.receipts_details, name='receipts_details'),
    url(r'^receipt/excel/(?P<pk>[-\S]+)/$$', views.excel_receipt, name='excel_receipt'),

    url(r'^receipt/api/getproduct/details$', views.get_product_data_id, name='get_product_data_id'),
    url(r'^receipt/api/getproduct/barcode$', views.get_product_data_barcode, name='get_product_data_barcode'),

    url(r'^receipt/delete/$', views.delete_purchase, name='delete_purchase'),

    url(r'^receiptlist/$', views.receipt_list, name='receipt_list'),
    url(r'^receiptlist/listall/$', views.all_receipts, name='all_receipts'),
    url(r'^receiptlist/metadata/$', views.receipts_metadata, name='receipts_metadata'),
    
    url(r'^receipt/paymentsave/$', views.payment_register, name='payment_register'),
    url(r'^paymentlist/$', views.payment_list, name='payment_list'),
    url(r'^paymentlistview/$', views.payment_list_view, name='payment_list_view'),
    
    url(r'^receipt/noninventory/$', views.purchase_receipt_new_noninventory, name='purchase_receipt_new_noninventory'),
    url(r'^receipt/noninventory/save/$', views.purchase_receipt_noninventory_save, name='purchase_receipt_noninventory_save'),

    url(r'^productinventorydetails/$', views.product_inventory_details, name='product_inventory_details'),
    
    # url(r'^debitnotereturn/$', views.debit_note_return_view, name='debit_note_return_view'),
    url(r'^return/noninventory/$', views.debit_note_new_noninventory, name='debit_note_return_view'),
    
    url(r'^purchase_graph/$', views.purchase_crossfilter, name='purchase_crossfilter'),
    url(r'^purchase_graph/data/$', views.receipts_crossfilter, name='receipts_crossfilter'),

    url(r'^hsnreport/$', views.get_hsn_report, name='get_hsn_report'),
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),

    url(r'^vendor-ledger/$', views.vendor_ledger, name='vendor_ledger'),
    url(r'^vendor-ledger/data/$', views.vendor_ledger_data, name='vendor_ledger_data'),

    url(r'^order/$', views.purchase_order_new, name='purchase_order_new'),
    url(r'^order/save/$', views.purchase_order_save, name='purchase_order_save'),
    url(r'^order/list/$', views.order_list_view, name='order_list_view'),
    url(r'^order/list/data/$', views.all_orders, name='all_orders'),
    url(r'^order/detailview/(?P<pk>[-\S]+)/$', views.order_detail_view, name='order_detail_view'),
    url(r'^order/detail/$', views.order_details, name='order_details'),
    url(r'^order/delete/$', views.order_delete, name='order_delete'),

]