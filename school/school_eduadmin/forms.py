from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)

from school_genadmin.models import Subject, class_group
from school_teacher.models import Teacher
from .models import Syllabus, Exam, class_section, classteacher, Examiner


class SyllabusForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (SyllabusForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['class_group'].queryset = class_group.objects.for_tenant(self.tenant).all()
		self.fields['subject'].queryset = Subject.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Syllabus
		fields =('class_group', 'subject', 'topics', 'year', )
	def clean(self):
		cd= super(SyllabusForm, self).clean()
		unique_key=cd.get('sub_key')
		unique_class=cd.get('class_group')
		unique_subject=cd.get('subject')
		unique_year=cd.get('year')
		error=[]
		key_blank=False
		subprod=""
		try:
			class_group=class_group.objects.filter(name=unique_class)
			subject=Subject.objects.filter(name=unique_name)
		except:
			data=None
		if not unique_key:
			key_blank=True
		if(data != None and not key_blank):
			try:
				syllabus=Syllabus.objects.filter(product=unique_product).filter(class_group=unique_class).\
						filter(subject=unique_subject).get(year=unique_key)
				self.add_error('subject',"Syllabus for same class group, subject and year already exists.")
			except:
				return cd
		raise forms.ValidationError(error)
		return cd



class ExamForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (ExamForm,self ).__init__(*args,**kwargs) # populates the post
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Exam
		fields = ('name', 'total', 'year','external_examiner')
	def clean(self):
		cd= super(ExamForm, self).clean()
		unique_name=cd.get('name')
		unique_year=cd.get('year')
		error=[]
		data=""
		if not unique_name:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				unique_key=unique_name+unique_year
				data=Exam.objects.for_tenant(self.tenant).get(key=unique_key)
				self.add_error('name',"Exam with same name and year already exists.")
				self.add_error('year',"Exam with same name and year already exists.")
			except:
				return cd
		return cd

class ClassTeacherForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (ClassTeacherForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['class_section'].queryset = class_section.objects.for_tenant(self.tenant).all()
		self.fields['class_teacher'].queryset = Teacher.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=classteacher
		fields = ('class_section', 'class_teacher', 'year',)
	def clean(self):
		cd= super(ClassTeacherForm, self).clean()
		unique_class=cd.get('class_section')
		unique_year=cd.get('year')
		error=[]
		data=""
		if not unique_class:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				class_selected=class_section.objects.for_tenant(self.tenant).get(name=unique_class)
				data=classteacher.objects.for_tenant(self.tenant).filter(class_section=class_selected).get(year=unique_year)
				self.add_error('class_section',"Class Teacher for the same class and year already exists.")
				self.add_error('year',"Class Teacher for the same class and year already exists.")
			except:
				return cd
		return cd


class ExaminerForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (ExaminerForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['class_section'].queryset = class_section.objects.for_tenant(self.tenant).all()
		self.fields['exam'].queryset = Exam.objects.for_tenant(self.tenant).all()
		self.fields['subject'].queryset = Subject.objects.for_tenant(self.tenant).all()
		self.fields['external_examiner'].queryset = Teacher.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=Examiner
		fields = ('class_section', 'exam', 'subject','external_examiner',)
	def clean(self):
		cd= super(ExaminerForm, self).clean()
		unique_class=cd.get('class_section')
		unique_exam=cd.get('exam')
		unique_subject=cd.get('subject')
		unique_teacher=cd.get('external_examiner')
		error=[]
		data=""
		if not (unique_class or unique_exam or unique_subject or unique_teacher):
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				class_selected=class_section.objects.for_tenant(self.tenant).get(name=unique_class)
				exam_selected=Exam.objects.for_tenant(self.tenant).get(name=unique_exam)
				subject_selected=Subject.objects.for_tenant(self.tenant).filter(name=unique_subject)
				data=Examiner.filter(class_section=class_selected).filter(exam=exam_selected).filter(subject=subject_selected)
				self.add_error('external_examiner',"Exam for this class and subject already has external examiner.")
			except:
				return cd
		return cd