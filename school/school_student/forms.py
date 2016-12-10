from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms import layout
from crispy_forms.layout import Submit, Layout, Field, Fieldset
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)
#from school_genadmin.models import Subject, class_group
#from school_teacher.models import Teacher
from .models import Student, student_guardian, student_education


class StudentForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (StudentForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper[0:1].wrap_together(Fieldset, 'Student Name')
		self.helper[2:3].wrap_together(Fieldset, 'Other Details')
		self.helper[4:10].wrap_together(Fieldset, 'Student Address')
		self.helper.layout.insert(4,layout.HTML(
  			'<p><i>Please fill this if you have some other student ID.<i></p>'))
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		# self.helper.layout[1][0].extend([
		# HTML("<p>whatever</p>"),
  #   	Div('add_field_on_the_go')
		# ])
		# self.helper.layout = Layout(
  #           PrependedText('local_id', '@', placeholder="username"),
  #       )
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Student
		fields =('first_name', 'last_name', 'contact', 'local_id', 'address_line_1', 'address_line_2','state','pincode' )
	

class StudentGuardianForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (StudentGuardianForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=student_guardian
		fields =('student', 'relation', 'first_name','last_name', 'contact', 'address', 'qualification', 'profession')

class StudentEducationForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (StudentEducationForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=student_education
		fields =('student', 'degree_name', 'institute', 'details', 'reward')