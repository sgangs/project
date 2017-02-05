from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.layout import Submit, Layout, Field, Fieldset
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)
#from school_genadmin.models import Subject, class_group
#from school_teacher.models import Teacher
from .models import Teacher

class DateInput(forms.DateInput):
    input_type = 'date'

class TeacherForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (TeacherForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		# self.helper[0:1].wrap_together(Fieldset, 'Student Name')
		# self.helper[2:3].wrap_together(Fieldset, 'Other Details')
		# self.helper[4:10].wrap_together(Fieldset, 'Student Address')
		# self.helper.layout.insert(4,layout.HTML(
  # 			'<p><i>Please fill this if you have some other student ID.<i></p>'))
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Teacher
		fields =('first_name', 'last_name', 'gender', 'blood_group','dob','joining_date', 'local_id', 'contact',\
		 			'email_id', 'address_line_1', 'address_line_2','state','pincode' )
		widgets = {
            'joining_date': DateInput(),
        }
	

class UploadFileForm(forms.Form):
	file = forms.FileField()
	def __init__(self,*args,**kwargs):
		super (UploadFileForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'