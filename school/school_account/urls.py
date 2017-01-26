from django.conf.urls import include,url
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from distributor.views import HomeView
from . import views
#from school_accountentry import views as detailsViews

urlpatterns = [
    url(r'^generic/$', views.base, {'input_type': 'Generic'},name='base'),
    url(r'^accountsbase/$', views.base, {'input_type': 'Accounts'},name='accounts_base'),
    url(r'^newperiod/$', views.account_new, {'input_type': 'Period'}, name='new_period'),
    url(r'^newledgergroup/$', views.account_new, {'input_type': 'Ledger Group'}, name='new_ledgergroup'),
    url(r'^newaccount/$', views.new_account, name='new_account'),
    #url(r'^newaccountyear/$', views.account_new, {'input_type': 'Account Year'}, name='new_account_year'),
    url(r'^newjournalgroup/$', views.account_new, {'input_type': 'Journal Group'}, name='new_journalgroup'),
    url(r'^newpaymentmode/$', views.payment_mode_new, {'input_type': 'Payment Mode'}, name='new_paymentmode'),
    url(r'^newjournalentry/$', views.journalentry, name='journalentry_new'),
    url(r'^ledgergrouplist/$', views.account_list, {'type': 'Ledger Group'},name='ledger_group_list'),
    url(r'^periodlist/$', views.account_list, {'type': 'Period'},name='period_list'),
    url(r'^accountlist/$', views.account_list, {'type': 'Account'},name='account_list'),
    url(r'^journalgrouplist/$', views.account_list, {'type': 'Journal Group'}, name='journalgroup_list'),
    url(r'^paymentmodelist/$', views.account_list, {'type': 'Payment Mode'},name='paymentmode_list'),
    url(r'^viewtrailbalance/$', views.trail_balance, name='view_trail_balance'),
    url(r'^viewincomeexpenditure/$', views.profit_loss, name='view_income_expenditure'),
    url(r'^viewbalancesheet/$', views.balance_sheet, name='view_balance_sheet'),
    url(r'^accountdetail/(?P<detail>[-\S]+)/$', views.account_detail, name='account_detail'),
    url(r'^journaldetail/(?P<detail>[-\S]+)/$', views.journal_detail, name='journal_detail'),
    #url(r'^calender/$', views.calender, name='calender'),
]