from django.conf.urls import include,url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^getstatelist/$', views.get_state_list, name='get_state_list'),

    url(r'^zone/getdata/$', views.zone_view, name='zone_view'),
    url(r'^zone/$', views.zone_data, name='zone_data'),
    
    url(r'^customer/getdata/$', views.customer_view, name='customer_view'),
    url(r'^customer/$', views.customer_data, name='customer_data'),
    url(r'^customer/format/$', views.customer_import_format, name='customer_import_format'),
    url(r'^uploadcustomer/$', views.import_customer, name='import_customer'),

    url(r'^vendor/getdata/$', views.vendor_view, name='vendor_view'),
    url(r'^vendor/$', views.vendor_data, name='vendor_data'),
    url(r'^vendor/autocomplete$', views.get_vendor_autocomplete, name='get_vendor_autocomplete'),
    # url(r'^uploadvendor/$', views.import_vendor, name='import_vendor'),
    
    
    url(r'^tax/getdata/$', views.tax_view, name='tax_view'),
    url(r'^tax/$', views.tax_data, name='tax_data'),
    url(r'^tax/individual/(?P<pk>[-\S]+)/$', views.individual_tax_view, name='individual_tax_view'),
    
    url(r'^dimensionunit/dimensiondata/$', views.dimension_view, name='dimension_view'),
    url(r'^dimensionunit/unitdata/$', views.unit_view, name='unit_view'),
    url(r'^dimensionunit/unitdata/onlybase/$', views.unit_base, name='unit_base'),
    url(r'^dimensionunit/$', views.dimension_unit_data, name='dimension_unit_data'),

    url(r'^manufacbrand/manufacdata/$', views.manufacturer_view, name='manufacturer_view'),
    url(r'^manufacbrand/branddata/$', views.brand_view, name='brand_view'),
    url(r'^manufacbrand/$', views.manufacbrand_data, name='manufacbrand_data'),

    url(r'^warehouse/getdata/$', views.warehouse_view, name='warehouse_view'),
    url(r'^warehouse/$', views.warehouse_data, name='warehouse_data'),
    
    url(r'^product/$', views.product_data, name='product_data'),
    url(r'^product/attributedata/$', views.attribute_view, name='attribute_view'),
    url(r'^product/productdata/$', views.product_view, name='product_view'),
    url(r'^product/productdetails/$', views.product_details, name='product_details'),
    url(r'^uploadproduct/$', views.import_product, name='import_product'),
    url(r'^product/format/$', views.product_import_format, name='product_import_format'),
    # url(r'^uploadproduct/$', views.import_product, name='import_product'),
]