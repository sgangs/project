from datetime import datetime

from distribution_user.models import User, Tenant
from distribution_accounts.models import accountChart, journalGroup 
from distribution_master.models import Dimension, Unit
 

#This function is used to create new journal groups
def create_journal_group(tenant, name):
    group=journalGroup()
    group.name=name
    group.tenant=tenant
    group.save()

#This function is used to create new accountChart
def create_accountChart(tenant, name, acc_type, remarks, key):
	account=accountChart()
	account.name=name
	account.account_type=acc_type
	account.remarks=remarks
	account.key=key
	account.tenant=tenant
	account.save()

#This function is used to create new Dimensions
def create_dimension(tenant, name, details):
	dimension=Dimension()
	dimension.name=name
	dimension.details=details
	dimension.tenant=tenant
	dimension.save()