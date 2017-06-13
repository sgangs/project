import datetime as dt
from datetime import datetime
from io import BytesIO
import xlsxwriter

from django.db import transaction
#from django.db.models import Avg, Sum, Max, Min
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext
# from school.id_definition import make_id
# from school_genadmin.models import Batch
from .models import Customer
from distributor.variable_list import state_list


def customer_validate(row, this_tenant):
    state_dict= dict((y,x) for x,y in state_list)
    # key=str(make_id())
    # item=None
    # row[12]=batch
    state_selected=row[4]
    row[4]=state_dict[state_selected]
    row.append(this_tenant)
    if (row[0] == None or row[0] == "" or row[1] == None or row[1] == "") :
        transaction.rollback()
        return HttpResponse("There is error in uploaded excel")
    return row

