from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm

from django.contrib.auth import (authenticate, get_user_model, password_validation,)
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (PrependedText, AppendedText)

from school_user.models import User, Tenant

class LoginForm(AuthenticationForm):
	# captcha = ReCaptchaField()
	pass
	

class revisedPasswordResetForm(PasswordResetForm):
	username= forms.CharField(label= ("Username"), max_length=50)
	email= forms.EmailField(label= ("Email"), max_length=254)
	captcha = ReCaptchaField()
	def __init__(self,*args,**kwargs):
		super (PasswordResetForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd = super(revisedPasswordResetForm, self).clean()
		username=cd.get('username')
		email=cd.get('email')
		error=[]
		try:
			user_username=User.objects.get(username=username)
			user_email=User.objects.get(email=email)
			if user_username != user_email:
				self.add_error('username','Username and email combination does not match')
				self.add_error('email','Username and email combination does not match')
		except:
			self.add_error('username',"Username or email does not exist.")	
			self.add_error('email',"Username or email does not exist.")
		
		return cd



