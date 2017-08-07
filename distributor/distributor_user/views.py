import json

from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import localtime
import json
#from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

# from .forms import *
from .models import *


@login_required
def tenant_settings(request):
	return render (request, 'tenant/settings_details.html')

def tenant_settings_data(request):
	response_data={}
	this_tenant=request.user.tenant
	response_data['name']=this_tenant.name
	response_data['gst']=this_tenant.gst
	response_data['dl_1']=this_tenant.dl_1
	response_data['dl_2']=this_tenant.dl_2
	response_data['address_1']=this_tenant.address_1
	response_data['address_2']=this_tenant.address_2
	response_data['state']=this_tenant.state
	response_data['city']=this_tenant.city
	response_data['pin']=this_tenant.pin

	jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)

