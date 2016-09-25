from django.conf.urls import url
from . import views
from distribution_accountsdetails import views as detailsViews

urlpatterns = [
    url(r'^base/$', views.accounts_base, name='base'),
    url(r'^periodlist/$', views.master_list, {'type': 'Period'},name='period_list'),
    url(r'^accountchartlist/$', views.master_list, {'type': 'Chart'},name='chart_list'),
    url(r'^journallist/$', views.journal_list,name='journal_list'),
    url(r'^newperiod/$', views.master_new, {'type': 'Period'}, name='period_new'),
    url(r'^newaccountchart/$', views.master_new, {'type': 'Chart'}, name='chart_new'),
    url(r'^newjournalentry/$', detailsViews.journalentry, name='journalentry_new'),
    url(r'^(?P<detail>[-\S]+)/$',views.account_detail, name='account_detail'),
]
