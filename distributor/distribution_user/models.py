

from django.db import models
from django.db.models import signals
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import datetime as dt
from datetime import datetime




account=(('Basic','Basic'),
			('SMS_Active','SMS_Active'))

paid=(('Yes','Yes'),
			('No','No'))



#This is the list of manufacturers
class Tenant(models.Model):
	name=models.CharField(max_length=50)
	address=models.CharField(max_length=200)
	cst=models.CharField("CST",max_length=20, blank=True)
	phone=models.CharField(max_length=20)
	#slug=models.SlugField(max_length=20)
	key=models.CharField(max_length=7, unique=True)
	registered_on=models.DateTimeField(null=True, blank=True)
	#details=models.TextField(blank=True)
	#email=models.EmailField('e-mail id',blank=True)
	account=models.CharField(max_length=12,choices=account,default='Basic')
	paid=models.CharField(max_length=12,choices=paid,default='Yes')


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
			#self.slug=slugify(self.emr_id)
			self.registered_on=timezone.now()
		#else:
		#	self.edited_on=timezone.now()

		super(Tenant, self).save(*args, **kwargs)
		
	def __str__(self):
		return self.name


class User(AbstractUser):
    tenant = models.ForeignKey(Tenant,related_name='user_tenant')
    user_id = models.CharField(max_length=14)

    def save(self, *args, **kwargs):
    	if not self.id:
    		data=self.tenant.key
    		today=dt.date.today()
    		length=len(data)+2
    		today_string=today.strftime('%y')
    		next_user_number='001'
    		last_user=type(self).objects.filter(user_id__contains=today_string).order_by('user_id').last()
    		if last_user:
    			last_user_number=int(last_user.user_id[length:])
    			next_user_number='{0:03d}'.format(last_user_number + 1)
    		self.user_id=data + today_string + next_user_number 
    		self.registered_on=timezone.now()

    	super(User, self).save(*args, **kwargs)
