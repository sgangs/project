from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^base/$', views.purchase_base, name='base'),
    url(r'^invoicelist/$', views.purchase_list, {'type': 'List'}, name='invoice_list'),
    url(r'^invoice/$', views.purchaseinvoice, {'type': 'New'}, name='invoice_new'),
    url(r'^invoicedue/$', views.purchase_due, {'type': 'Due'}, name='invoice_due'),
    url(r'^vendordue/$', views.vendor_due, {'type': 'Due List'}, name='vendor_due'),
	url(r'^inventoryreturn/$', views.inventory_return, name='inventory_return'),    
    url(r'^(?P<detail>[-\S]+)/due/$',views.purchase_detail, {'type': 'Due'}, name='invoice_detail_due'),
    url(r'^(?P<detail>[-\S]+)/$',views.purchase_detail, {'type': 'Detail'}, name='invoice_detail'),
    
]