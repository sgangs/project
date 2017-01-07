from django.db import IntegrityError, transaction
import json
from school_user.models import Tenant
from school_account.models import Account
from school_genadmin.models import class_group
from .models import monthly_fee, monthly_fee_list, yearly_fee, yearly_fee_list
# fee_structure, fee_structure_list,
#This function is used to provide students' data for attendance/exam score entry
def create_fee_structure(request, fee_type):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            #create_fee_structure(request, fee_type)
            feename=request.POST.get('feename')
            fee_lists = json.loads(request.POST.get('details'))
            # months = json.loads(request.POST.get('months'))
            if (fee_type == 'Monthly'):
                fee_create=monthly_fee()
            else:
                fee_create=yearly_fee()
                month=request.POST.get('month')
                fee_create.month=month
            fee_create.name=feename
            # for month in months:
            #     if (month.name == 'Jan'):
            #         if (month.value):
            #             jan_1==True
            #         else
            #             jan_1==False
            #     elif (month.name == 'Feb'):
            #         if (month.value):
            #             jan_1==True
            #         else
            #             jan_1==False
            fee_create.tenant=this_tenant
            fee_create.save()
            for data in fee_lists:
                accountid=data['account']
                amount=float(data['amount'])
                account=Account.objects.get(id=accountid)
                if (fee_type == 'Monthly'):
                    fee_list=monthly_fee_list()
                    fee_list.monthly_fee=fee_create
                else:
                    fee_list=yearly_fee_list()
                    fee_list.yearly_fee=fee_create
                fee_list.account = account
                fee_list.name = account.name
                fee_list.amount= amount                                   
                fee_list.tenant=this_tenant
                fee_list.save()
        except:
            transaction.rollback()


