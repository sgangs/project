from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^landing/$', views.landing, name='landing'),
    url(r'^listbase/$', views.master_base, {'type': 'List'},name='list_base'),
    url(r'^newbase/$', views.master_base, {'type': 'New'},name='new_base'),
    url(r'^manufacturerlist/$', views.master_list, {'type': 'Manufacturer'},name='manufacturer_list'),
    url(r'^unitlist/$', views.master_list, {'type': 'Unit'},name='unit_list'),
    url(r'^productlist/$', views.master_list, {'type': 'Product'},name='product_list'),
    url(r'^zonelist/$', views.master_list, {'type': 'Zone'},name='zone_list'),
    url(r'^customerlist/$', views.master_list, {'type': 'Customer'},name='customer_list'),
    url(r'^vendorlist/$', views.master_list, {'type': 'Vendor'},name='vendor_list'),
    url(r'^warehouselist/$', views.master_list, {'type': 'Warehouse'},name='warehouse_list'),
    #url(r'^accountlist/$', views.master_list, {'type': 'Account'},name='account_list'),
    #url(r'^subproductlist/$', views.master_list, {'type': 'subProduct'},name='subproduct_list'),
    url(r'^newmanufacturer/$', views.master_new, {'type': 'Manufacturer'}, name='manufacturer_new'),
    url(r'^newunit/$', views.master_new, {'type': 'Unit'}, name='unit_new'),
    url(r'^newproduct/$', views.new_product, {'type': 'Product'}, name='product_new'),
    url(r'^newsubproduct/$', views.new_subproduct, {'type': 'subProduct'}, name='subproduct_new'),
    url(r'^newzone/$', views.master_new, {'type': 'Zone'}, name='zone_new'),
    url(r'^newcustomer/$', views.new_customer, {'type': 'Customer'}, name='customer_new'),
    url(r'^newvendor/$', views.master_new, {'type': 'Vendor'}, name='vendor_new'),
    url(r'^newwarehouse/$', views.new_warehouse, {'type': 'Warehouse'}, name='warehouse_new'),
    #url(r'^newaccount/$', views.master_new, {'type': 'Account'}, name='account_new'),
    url(r'^(?P<detail>([-\S])+)/$',views.master_detail, name='detail'),
]