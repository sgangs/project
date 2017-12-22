import json

import phonenumbers

from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.password_validation import *
from django.core.validators import validate_email
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import localtime
#from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from rest_framework.decorators import api_view
from rest_framework.response import Response

# from .forms import *
from .models import *


@login_required
def tenant_settings(request):
	return render (request, 'tenant/settings_details.html')

@login_required
@api_view(['GET','POST'],)
def tenant_settings_data(request):
	response_data={}
	this_tenant=request.user.tenant
	if request.method == 'GET':
		response_data['name']=this_tenant.name
		response_data['gst']=this_tenant.gst
		response_data['pan']=this_tenant.pan
		# response_data['pan']=this_tenant.pan
		response_data['dl_1']=this_tenant.dl_1
		response_data['dl_2']=this_tenant.dl_2
		response_data['address_1']=this_tenant.address_1
		response_data['address_2']=this_tenant.address_2
		response_data['state']=this_tenant.state
		response_data['city']=this_tenant.city
		response_data['pin']=this_tenant.pin
		response_data['distributor_sales_policy']=this_tenant.distributor_sales_policy

	elif request.method == 'POST':
		gst = request.data.get('gst')
		pan = request.data.get('pan')
		dl_1 = request.data.get('dl_1')
		dl_2 = request.data.get('dl_2')
		# address_1 = request.data.get('address_1')
		# address_2 = request.data.get('address_2')
		# address_2 = request.data.get('address_2')
		# pin = request.data.get('pin')
		try:
			distributor_sales_policy = json.loads(request.data.get('distributor_sales_policy'))
		except:
			distributor_sales_policy = []
		
		this_tenant.gst = gst
		this_tenant.pan = pan
		this_tenant.dl_1 = dl_1
		this_tenant.dl_2 = dl_2
		this_tenant.distributor_sales_policy = distributor_sales_policy
		this_tenant.save()

	jsondata = json.dumps(response_data,  cls=DjangoJSONEncoder)
	return HttpResponse(jsondata)


@api_view(['GET',],)
def user_list(request):
	# this_tenant=request.user.tenant
	# students_login_count=Student.objects.for_tenant(this_tenant).filter(isactive=True).exclude(user=None).count()
	# profiles_allowed=this_tenant.no_of_profile
	# if (profiles_allowed<=students_login_count):
		# return HttpResponse("You cannot create any more student profile")
	return render(request,'tenant/user_list.html', {'extension': 'base.html'})

@api_view(['GET','POST',],)
def user_list_data(request):
	this_tenant=request.user.tenant
	if request.method == 'GET':
		response_data = {}
		calltype = request.GET.get('calltype')
		if (calltype == 'get_users'):
			users = list(User.objects.filter(tenant = this_tenant).all().\
					values('first_name', 'last_name', 'id', 'username', 'email', 'user_type', 'aadhaar_no'))
			response_data = users
		elif (calltype == 'check_username'):
			username = request.GET.get('username')
			try:
				user=User.objects.get(username=username)
				response_data['error'] = "Username exist"
			except:
				response_data['error'] = "Username does not exist"

		elif (calltype == 'check_email'):
			email = request.GET.get('email')
			try:
				validate_email(email)
				user=User.objects.get(email=email)
				response_data['error'] = "Email exist"
			except Exception as err:
				if (str(err) == "['Enter a valid email address.']" ):
					response_data['error'] = "Email address is not valid"
				else:
					response_data['error'] = "Email does not exist"

		# elif (calltype == 'check_password'):
		# 	password = request.GET.get('password')
		# 	try:
		# 		validate_password(password)
		# 		response_data['error'] = "No error"
		# 	except Exception as err:
		# 		print (err)
		# 		response_data['error'] = 'error'

		# elif (calltype == 'check_phone'):
		# 	phone = request.GET.get('phone')
		# 	try:
		# 		print("Phone no is: "+phone)
		# 		parsed_phone = phonenumbers.parse(phone, None)
		# 		print(parsed_phone)
		# 		print(phonenumbers.is_valid_number(parsed_phone))
		# 	except Exception as err:
		# 		print(err)

		jsondata = json.dumps(response_data)
		return HttpResponse(jsondata)

	if request.method == 'POST':
		this_tenant = request.user.tenant
		calltype = request.data.get('calltype')
		response_data = {}
		if (calltype == 'newuser'):
			with transaction.atomic():
				try:
					username = request.data.get('username')
					password = request.data.get('password')
					repeat = request.data.get('repeat')
					email = request.data.get('email')
					firstname = request.data.get('firstname')
					lastname = request.data.get('lastname')
					phone = request.data.get('phone')
					user_types = json.loads(request.data.get('user_permissions'))
					if (len(phone) > 0):
						try:
							parsed_phone = phonenumbers.parse(phone, None)
							if not phonenumbers.is_valid_number(parsed_phone):
								response_data['error'] = "Phone number not valid"
								jsondata = json.dumps(response_data)
								return HttpResponse(jsondata)
						except:
							print("error in phone")
							response_data['error'] = "Phone number not valid"
							jsondata = json.dumps(response_data)
							return HttpResponse(jsondata)
					try:
						validate_email(email)
					except:
						response_data['error'] = "Email not valid"
						jsondata = json.dumps(response_data)
						return HttpResponse(jsondata)
					if (password != repeat):
						response_data['error'] = "Password Match Error"
						jsondata = json.dumps(response_data)
						return HttpResponse(jsondata)
					user=User()
					user.username=username
					user.user_type=user_types
					user.first_name=firstname
					user.last_name=lastname
					if (email == "" or email == None):
						response_data['error'] = "Email is None error"
						jsondata = json.dumps(response_data)
						return HttpResponse(jsondata)
					else:
						user.email=email
					user.phone = phone
					user.user_type = user_types
					user.set_password(password)
					user.tenant=this_tenant
					user.save()
				except:
					transaction.rollback()
			jsondata = json.dumps(response_data)
			return HttpResponse(jsondata)