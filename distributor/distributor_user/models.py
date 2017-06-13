import datetime as dt
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

from rest_framework.authtoken.models import Token

from distributor.variable_list import state_list, account, user_type

#This is the list of schools. Add paid until model and get it to work with decorators
class Tenant(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField('Name of your company',max_length=50)
	pan=models.PositiveIntegerField("PAN Number", blank=True, null=True)
	tin=models.PositiveIntegerField("TIN Number", blank=True, null=True)
	cst=models.PositiveIntegerField("CST Number", blank=True, null=True)
	gst=models.PositiveIntegerField("GST Number", blank=True, null=True)
	address_1=models.CharField("Address Line 1",max_length=200)
	address_2=models.CharField("Address Line 2", max_length=200, blank=True, null=True)
	state=models.CharField(max_length=4,choices=state_list)
	city=models.CharField("City", max_length=50)
	pin=models.CharField("Pincode", max_length=8)
	email=models.EmailField("Official Email Address",unique=True)
	phone=PhoneNumberField()
	slug=models.SlugField(max_length=20)
	key=models.CharField("Unique ID/Short Name of Company",max_length=20, unique=True)
	registered_on=models.DateTimeField()
	#no_of_registered_students_allowed
	no_of_profile=models.PositiveIntegerField(default=0)	
	account=models.CharField(max_length=12,choices=account,default='Basic')
	maintain_inventory=models.BooleanField('Do you want to maintain inventory', default=True)
	paid=models.BooleanField('Has the tenant paid?')
	trial=models.BooleanField('Is the tenant under trail?')
	trial_from=models.DateField(null=True, blank=True)
	trial_to=models.DateField(null=True, blank=True)
	paid_until=models.DateField(null=True, blank=True)
	is_active=models.BooleanField(default=True)

	def save(self, *args, **kwargs):
		if not self.id:
			self.registered_on = timezone.now()
			self.slug=slugify(self.key)
		#else:
		#	self.edited_on=timezone.now()

		super(Tenant, self).save(*args, **kwargs)
		
	def __str__(self):
		return self.name

#This is the individual user module
class User(AbstractUser):
	id=models.BigAutoField(primary_key=True)
	aadhaar_no=models.CharField("Aadhaar Number", blank=True, max_length=20)
	tenant = models.ForeignKey(Tenant,related_name='user_tenant')
	phone=PhoneNumberField("Phone Number")
	user_type=models.CharField(max_length=10,choices=user_type)
    #registered_on=models.DateTimeField(null=True, blank=True)


class user_permission(models.Model):
	id=models.BigAutoField(primary_key=True)
	tenant = models.ForeignKey(Tenant,related_name='userPermission_tenant')
	user = models.ForeignKey(Tenant,related_name='userPermission_user')
	#create is for:create, update, delete.
	#For all master models
	can_create_master=models.BooleanField()
	can_authorize_master=models.BooleanField()
	#For all purchase models
	can_create_purchase=models.BooleanField()
	can_authorize_purchase=models.BooleanField()
	#For all sales models
	can_create_sales=models.BooleanField()
	can_authorize_sales=models.BooleanField()
	#For all accounts models
	can_create_sales=models.BooleanField()
	can_authorize_sales=models.BooleanField()



# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)

