import datetime as dt
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField

from rest_framework.authtoken.models import Token

from distributor.variable_list import state_list, account, user_type, tenant_type

class TenantManager(models.Manager):
	def for_tenant(self, tenant):
		return self.get_queryset().filter(tenant=tenant)

#This is the list of schools. Add paid until model and get it to work with decorators
class Tenant(models.Model):
	id=models.BigAutoField(primary_key=True)
	name=models.CharField('Name of your company',max_length=50)
	tenant_type=models.PositiveSmallIntegerField(default=1, choices=tenant_type)
	pan=models.CharField("PAN Number",max_length=20, blank=True, null=True)
	tin=models.CharField("TIN Number",max_length=20, blank=True, null=True)
	# cst=models.PositiveIntegerField("CST Number", blank=True, null=True)
	gst=models.CharField("GST Number",max_length=20,  blank=True, null=True)
	dl_1=models.CharField("Drug License 1",max_length=10,  blank=True, null=True)
	dl_2=models.CharField("Drug License 2",max_length=10,  blank=True, null=True)

	# pan=models.CharField("PAN Number",max_length=20, blank=True, null=True)
	# tin=models.CharField("TIN Number",max_length=20, blank=True, null=True)
	# cst=models.CharField("CST Number",max_length=20, blank=True, null=True)
	# gst=models.CharField("GST Number",max_length=20, blank=True, null=True)

	distributor_sales_policy=ArrayField(models.TextField(), blank=True, null=True)

	address_1=models.CharField("Address Line 1",max_length=100)
	address_2=models.CharField("Address Line 2", max_length=100, blank=True, null=True)
	state=models.CharField(max_length=4,choices=state_list)
	city=models.CharField("City", max_length=30)
	pin=models.CharField("Pincode", max_length=8)
	email=models.EmailField("Official Email Address",unique=True)
	phone=PhoneNumberField()
	slug=models.SlugField(max_length=20)
	key=models.CharField("Unique ID/Short Name of Company",max_length=20, unique=True)
	registered_on=models.DateTimeField()
	#no_of_registered_users_allowed
	no_of_profile=models.PositiveSmallIntegerField(default=0)	
	account=models.CharField(max_length=12,choices=account,default='Basic')
	maintain_inventory=models.BooleanField('Do you want to maintain inventory', default=True)
	paid=models.BooleanField('Has the tenant paid?')
	trial=models.BooleanField('Is the tenant under trail?')
	trial_from=models.DateField(null=True, blank=True)
	trial_to=models.DateField(null=True, blank=True)
	paid_due=models.DateField(null=True, blank=True) #Next payment due on
	is_active=models.BooleanField(default=True)
	updated = models.DateTimeField(auto_now=True)

	# sms_left=models.PositiveIntegerField(default=0)

	def save(self, *args, **kwargs):
		if not self.id:
			self.registered_on = timezone.now()
			self.slug=slugify(self.key)
		#else:
		#	self.edited_on=timezone.now()

		super(Tenant, self).save(*args, **kwargs)
		
	def __str__(self):
		return self.name

class tenant_payment(models.Model):
	id=models.BigAutoField(primary_key=True)
	tenant = models.ForeignKey(Tenant,related_name='tenantPayment_tenant')
	amount_paid=models.DecimalField(max_digits=12, decimal_places=2)
	# cgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	# sgsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	# igsttotal=models.DecimalField(max_digits=12, decimal_places=2, default=0)
	payment_no=models.BigIntegerField()
	is_processed=models.BooleanField(default=False)
	paid_on=models.DateField(blank=True, null=True)
	no_customers=models.PositiveSmallIntegerField(default=1)
	no_sms=models.PositiveSmallIntegerField(default=0)


#This is the individual user module
#User type has to be an arrayfield with the option of multiple fields - the list of permissions an user can have.
class User(AbstractUser):
	id=models.BigAutoField(primary_key=True)
	aadhaar_no=models.CharField("Aadhaar Number", blank=True, max_length=20)
	tenant = models.ForeignKey(Tenant,related_name='user_tenant')
	phone=PhoneNumberField("Phone Number")
	# user_type=models.CharField(max_length=10,choices=user_type)
	#Options for user type - "master", "retail_sales", "retail_sales_lead", "retail_sales", "distributor_sales", "distributor_sales_lead"
	#"service_sales", "service_sales_lead", "purchase", "purchase_lead", "overall_lead"

	user_type=ArrayField(models.CharField(max_length=20), blank=True, null=True)
	#registered_on=models.DateTimeField(null=True, blank=True)
	updated = models.DateTimeField(auto_now=True)
	# objects = TenantManager()
	
	class Meta(object):
		unique_together = ('email',)

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)

