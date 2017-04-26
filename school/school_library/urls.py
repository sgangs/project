from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views

urlpatterns = [
    #url(r'^base/$', views.base, name='base'),
    url(r'^newlibrary/$', views.library_new, {'input_type': 'Library'}, name='new_library'),
    url(r'^newbook/$', views.library_new, {'input_type': 'Book'}, name='new_book'),
    url(r'^newperiod/$', views.library_new, {'input_type': 'Period'}, name='new_period'),
    url(r'^booklist/$', views.library_list, {'input_type': 'Book'}, name='book_list'),
    url(r'^bookissue/$', views.book_issue, name='book_issue'),
    url(r'^booklist/book/(?P<detail>[-\S]+)/$',views.library_edit, name='library_edit'),
    #url(r'^(?P<detail>[-\S]+)/$',views.purchase_detail, {'type': 'Detail'}, name='invoice_detail'),
]

