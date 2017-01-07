from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)

from school_genadmin.models import Subject, class_group
from school_teacher.models import Teacher
from .models import Library, Book, issue_period


class DateInput(forms.DateInput):
    input_type = 'date'

class LibraryForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (LibraryForm,self ).__init__(*args,**kwargs) # populates the post
		#self.fields['class_group'].queryset = class_group.objects.for_tenant(self.tenant).all()
		#self.fields['subject'].queryset = Subject.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Library
		fields =('room', )
	def clean(self):
		cd= super(LibraryForm, self).clean()
		unique_room=cd.get('room')
		error=[]
		if not unique_key:
			raise forms.ValidationError(error)
		if(data != None and not key_blank):
			try:
				room=Library.objects.for_tenant(self.tenant).get(room=unique_room)
				self.add_error('room',"Library with same room number/name already exists.")
			except:
				return cd
		raise forms.ValidationError(error)
		return cd


class BookForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (BookForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['library'].queryset = Library.objects.for_tenant(self.tenant).all()
		self.fields['subject'].queryset = Subject.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Book
		fields =('name','author','publisher',\
				'edition','isbn','remark','subject','library', 'location','purchased_on','price','school_book_code')
		widgets = {
            'purchased_on': DateInput(),
        }
	# def clean(self):
	# 	cd= super(BookForm, self).clean()
	# 	unique_room=cd.get('room')
	# 	error=[]
	# 	if not unique_key:
	# 		raise forms.ValidationError(error)
	# 	if(data != None and not key_blank):
	# 		try:
	# 			room=Library.objects.for_tenant(self.tenant).get(room=unique_room)
	# 			self.add_error('room',"Library with same room number/name already exists.")
	# 		except:
	# 			return cd
	# 	raise forms.ValidationError(error)
	# 	return cd

class PeriodForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (PeriodForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=issue_period
		fields =('period', )
	# def clean(self):
	# 	cd= super(PeriodForm, self).clean()
	# 	unique_room=cd.get('room')
	# 	error=[]
	# 	if not unique_key:
	# 		raise forms.ValidationError(error)
	# 	if(data != None and not key_blank):
	# 		try:
	# 			room=Library.objects.for_tenant(self.tenant).get(room=unique_room)
	# 			self.add_error('room',"Library with same room number/name already exists.")
	# 		except:
	# 			return cd
	# 	raise forms.ValidationError(error)
	# 	return cd