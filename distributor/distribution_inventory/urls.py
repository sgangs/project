from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list/$', views.inventoryList, name='list'),
    url(r'^returnablelist/$', views.returnableInventoryList, name='returnable_list'),
    url(r'^damagedlist/$', views.damagedInventoryList, name='damaged_list'),
]
