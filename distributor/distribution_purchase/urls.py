from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^base/$', views.purchase_base, name='base'),
    url(r'^invoicelist/$', views.purchase_list, {'type': 'List'}, name='invoice_list'),
    url(r'^invoice/$', views.purchaseinvoice, {'type': 'New'}, name='invoice_new'),
    url(r'^(?P<detail>[-\S]+)/$',views.purchase_detail, {'type': 'Detail'}, name='invoice_detail'),
    
]