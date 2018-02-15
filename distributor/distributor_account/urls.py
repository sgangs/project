from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^getaccounttype/$', views.get_account_type, name='get_account_type'),
    url(r'^payment-mode/getdata/$', views.payment_mode_view, name='payment_mode_view'),
    url(r'^payment-mode/$', views.payment_mode_data, name='payment_mode_data'),
    url(r'^account/data/$', views.account_details_view, name='account_details_view'),
    
    url(r'^account-accountyear/data/$', views.get_account_account_year, name='get_account_account_year'),

    
    url(r'^tax-report/getdata/$', views.get_tax_report, name='get_tax_report'),
    url(r'^tax-report/$', views.new_tax_report, name='new_tax_report'),
    url(r'^tax-report/shortsummary/$', views.tax_short_summary, name='tax_short_summary'),
    # url(r'^tax-report/download/$', views.download_tax_report, name='download_tax_report'),
    url(r'^tax-report/(?P<fromdate>\d{4}-\d{2}-\d{2})/(?P<todate>\d{4}-\d{2}-\d{2})/(?P<report_type>[\w\-]+)/$', views.download_tax_report,\
                        name='download_tax_report'), 
    url(r'^tax-report/shortsummary/$', views.tax_short_summary, name='tax_short_summary'),


    url(r'^account/$', views.account_data, name='account_data'),
    url(r'^info/$', views.account_info_view, name='account_info_view'),
    url(r'^ledgergroup/getdata/$', views.ledger_group_view, name='ledger_group_view'),
    url(r'^journalgroup/getdata/$', views.journal_group_view, name='journal_group_view'),
    url(r'^newjournalentry/$', views.new_journal_entry, name='new_journal_entry'),
    url(r'^newjournalentry/data/$', views.journal_entry_data, name='journal_entry_data'),
    url(r'^accountperiod/$', views.account_period_view, name='account_period_view'),
    url(r'^accountperiod/data/$', views.account_period_data, name='account_period_data'),

    url(r'^trialbalance/data/$', views.trial_balance_data, name='trial_balance_data'),
    url(r'^trialbalance/$', views.trial_balance_view, name='trial_balance_view'),
    url(r'^profitloss/$', views.profit_loss_view, name='profit_loss_view'),
    url(r'^balancesheet/$', views.balance_sheet, name='balance_sheet'),
    # url(r'^invoice/api/getproduct$', views.get_product, name='get_product'),
    # url(r'^eventdetail/(?P<detail>[-\S]+)/$', views.classdetail, name='class_detail'),
    url(r'^gst-purchase-report/getdata/$', views.get_gst_purchase, name='get_gst_purchase'),
    url(r'^gst-purchase-report/$', views.new_gst_purchase, name='new_gst_purchase'),
    # url(r'^journallist/account/(?P<pk_detail>[-\S]+)/$', views.account_journal_entries, name='account_journal_entries'),
    url(r'^journallist/account/(?P<pk_detail>[-\S]+)/$', views.account_journal_entries_view, name='account_journal'),
    url(r'^journallist/account-list/$', views.account_journal_entries_data, name='account_journal'),
    url(r'^journalview/(?P<pk_detail>[-\S]+)/$', views.journal_detail, name='journal_detail'),
    
    url(r'^gst-payment/$', views.gst_payment, name='gst_payment'),

    url(r'^customerpending/$', views.customer_pending, name='customer_pending'),
]