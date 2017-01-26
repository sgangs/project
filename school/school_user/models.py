import datetime as dt
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager



account=(('Basic','Basic'),
			('SMS_Active','SMS_Active'))

user_type=(('Master','Master'),
			('Account','Account'),
			('Admin','Admin'),
			('Teacher','Teacher'),
			('Student','Student'),
			('Parent','Parent'))

#This is the list of schools. Add paid until model and get it to work with decorators
class Tenant(models.Model):
	name=models.CharField(max_length=50)
	address=models.CharField(max_length=200)
	email=models.EmailField(unique=True)
	#cst=models.CharField("CST",max_length=20, blank=True, null=True)
	#vat=models.CharField("VAT",max_length=20, blank=True, null=True)
	#tin=models.CharField("TIN",max_length=20, blank=True, null=True)
	phone=models.CharField(max_length=20)
	slug=models.SlugField(max_length=20)
	key=models.CharField("Unique key for School",max_length=20, unique=True)
	registered_on=models.DateTimeField(default=datetime.now())
	#details=models.TextField(blank=True)
	#email=models.EmailField('e-mail id',blank=True, null=True)
	account=models.CharField(max_length=12,choices=account,default='Basic')
	paid=models.BooleanField('Has the tenant paid?')
	trail=models.BooleanField('Is the tenant under trail?')
	paid_until=models.DateField(null=True, blank=True)

	def save(self, *args, **kwargs):
		if not self.id:
			#data="emr"
			#today=dt.date.today()
			#today_string=today.strftime('%y%m%d')
			#next_emr_number='001'
			#last_emr=type(self).objects.filter(emr_id__contains=today_string).order_by('emr_id').last()
			#if last_emr:
			#	last_emr_number=int(last_emr.emr_id[9:])
			#	next_emr_number='{0:03d}'.format(last_emr_number + 1)
			#self.emr_id=data + today_string + next_emr_number 
			self.slug=slugify(self.key)
		#else:
		#	self.edited_on=timezone.now()

		super(Tenant, self).save(*args, **kwargs)
		
	def __str__(self):
		return self.name

#This is the individual user module
class User(AbstractUser):
    tenant = models.ForeignKey(Tenant,default=2,related_name='user_tenant')
    #user_id = models.CharField(max_length=30)
    user_type=models.CharField(max_length=10,choices=user_type)
    #registered_on=models.DateTimeField(null=True, blank=True)

    # def save(self, *args, **kwargs):
    # 	if not self.id:
    # 		data=self.tenant.key
    # 		today=dt.date.today()
    # 		length=len(data)+2
    # 		today_string=today.strftime('%y')
    # 		next_user_number='0001'
    # 		last_user=type(self).objects.filter(tenant=self.tenant).filter(user_id__contains=today_string).order_by('user_id').last()
    # 		if last_user:
    # 			last_user_number=int(last_user.user_id[length:])
    # 			next_user_number='{0:04d}'.format(last_user_number + 1)
    # 		self.user_id=data + today_string + next_user_number 
    # 		self.registered_on=timezone.now()
    # 	super(User, self).save(*args, **kwargs)
