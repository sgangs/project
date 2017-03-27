from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (PrependedText, AppendedText)

from .models import Subject, class_group, House, Batch, academic_year, notice_board

#This is for using date widget
class DateInput(forms.DateInput):
    input_type = 'date'


#This for is to adding new subject
class SubjectForm(forms.ModelForm):
	class Meta:
		model=Subject
		fields = ('name',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(SubjectForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(SubjectForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=Subject.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"Subject with name already exists.")
			except:
				return cd
		return cd

#This for is to adding new subject
class academicYearForm (forms.ModelForm):
	class Meta:
		model=academic_year
		fields = ('year','start','end','current_academic_year')
		widgets = {
            'start': DateInput(),
            'end': DateInput(),
        }
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(academicYearForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(academicYearForm, self).clean()
		year=cd.get('year')
		start=cd.get('start')
		end=cd.get('end')
		error=[]
		data=""
		if not year:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=academic_year.objects.for_tenant(self.tenant).get(year=year)
				self.add_error('year',"Academic Session with same data already exist")
			except:
				pass
			try:
				data=academic_year.objects.for_tenant(self.tenant).get(start=start)
				self.add_error('start',"Academic Session with same data already exist")
			except:
				pass
			try:
				data=academic_year.objects.for_tenant(self.tenant).get(end=end)
				self.add_error('end',"Academic Session with same data already exist")
			except:
				return cd
		return cd

#This for is to adding new batch
class BatchForm(forms.ModelForm):
	class Meta:
		model=Batch
		fields = ('start_year','end_year')
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(BatchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(BatchForm, self).clean()
		start_year=cd.get('start_year')
		end_year=cd.get('end_year')
		error=[]
		data=""
		if start_year and end_year:
			try:
				datas=Batch.objects.for_tenant(self.tenant).get(start_year=start_year)
				datae=Batch.objects.for_tenant(self.tenant).get(end_year=end_year)
				self.add_error('start_year',"Batch with same start and end year exist.")
				self.add_error('end_year',"Batch with same start and end year exist.")
			except:
				pass
			try:
				if (int(start_year)<1980 or int(start_year)>2050):
					self.add_error('start_year',"As of now, batch much start between 1980 and 2050.")
			except:
				self.add_error('start_year',"This must be a year.")
			try:
				if (int(end_year)<1980 or int(end_year)>2050):
					self.add_error('end_year',"As of now, batch much end between 1980 and 2050.")
			except:
				self.add_error('end_year',"This must be a year.")
		return cd

#This for is to adding new class group
class classGroupForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (classGroupForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=class_group
		fields = ('name','standard')
	def clean(self):
		cd= super(classGroupForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=class_group.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"Class Group with same name already exists.")
			except:
				return cd
		return cd


class HouseForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (HouseForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=House
		fields = ('name', 'house_motto',)
	def clean(self):
		cd= super(HouseForm, self).clean()
		unique_name=cd.get('name')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=House.objects.for_tenant(self.tenant).get(name=unique_name)
				self.add_error('name',"House with same key already exists.")
			except:
				return cd
		return cd

class NoticeForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (NoticeForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=notice_board
		fields = ('title', 'details','show_from')
		widgets = {
            'show_from': DateInput(),
        }

	# def clean(self):
	# 	cd= super(NoticeForm, self).clean()
	# 	unique_name=cd.get('name')
	# 	error=[]
	# 	data=""
	# 	if not unique_name:
	# 		raise forms.ValidationError(error)
	# 		return cd
	# 	else:
	# 		try:
	# 			data=House.objects.for_tenant(self.tenant).get(name=unique_name)
	# 			self.add_error('name',"House with same key already exists.")
	# 		except:
	# 			return cd
	# 	return cd