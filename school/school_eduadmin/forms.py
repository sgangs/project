from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, AppendedText)

from school_genadmin.models import Subject, class_group
from school_teacher.models import Teacher
from school_student.models import Student
from .models import Syllabus, Exam, class_section, classteacher, Examiner, classstudent, subject_teacher, total_period


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
		unique_class=cd.get('class_group')
		unique_subject=cd.get('subject')
		unique_year=cd.get('year')
		topics=cd.get('topics')
		error=[]
		try:
			syllabus=Syllabus.objects.for_tenant(self.tenant).filter(class_group=unique_class,subject=unique_subject)\
					.get(year=unique_year)
			self.add_error('subject',"Syllabus for same class group, subject and year already exists.")
			self.add_error('year',"Syllabus for same class group, subject and year already exists.")
		except:
			return cd
			
		return cd

class SubjectTeacherForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (SubjectTeacherForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['class_section'].queryset = class_section.objects.for_tenant(self.tenant).all()
		self.fields['subject'].queryset = Subject.objects.for_tenant(self.tenant).all()
		self.fields['teacher'].queryset = Teacher.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=subject_teacher
		fields =('class_section', 'subject', 'teacher', 'year', )
	def clean(self):
		cd= super(SubjectTeacherForm, self).clean()
		unique_class=cd.get('class_section')
		unique_subject=cd.get('subject')
		unique_year=cd.get('year')
		teacher=cd.get('teacher')
		error=[]
		try:
			if (unique_subject and unique_class and unique_year and teacher):
				class_group=unique_class.classgroup
				try:
					issubject=Syllabus.objects.for_tenant(self.tenant).filter(class_group=class_group,subject=unique_subject)\
						.get(year=unique_year)
				except:
					self.add_error('subject',"Class does not have selected subject.")
					self.add_error('class_section',"Class does not have selected subject.")
				data = subject_teacher.objects.filter(class_section=unique_class,subject=unique_subject,\
					year=unique_year).get(teacher=teacher)
				self.add_error('subject',"Class, subject has the same teacher for selected year.")
				self.add_error('class_section',"Class, subject has the same teacher for selected year.")
				self.add_error('teacher',"Class, subject has the same teacher for selected year.")
				self.add_error('year',"Class, subject has the same teacher for selected year.")
		except:
			return cd		
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
		if not (unique_class or unique_year):
			raise forms.ValidationError(error)
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
		else:
			try:
				#Examiner check to be performed: Check if subject is part of class. Check if examiner is already subject teacher.
				class_selected=class_section.objects.for_tenant(self.tenant).get(name=unique_class)
				class_group=class_selected.class_group
				exam_selected=Exam.objects.for_tenant(self.tenant).get(name=unique_exam)
				year=exam_selected.year
				subject_selected=Subject.objects.for_tenant(self.tenant).filter(name=unique_subject)
				data=Examiner.filter(class_section=class_selected,exam=exam_selected, subject=subject_selected)
				self.add_error('external_examiner',"Exam for this class and subject already has external examiner.")
			except:
				return cd
		return cd

#This form will add one student to class. This has to be changed soon.
class ClassStudentForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super (ClassStudentForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['class_section'].queryset = class_section.objects.for_tenant(self.tenant).all()
		self.fields['student'].queryset = Student.objects.for_tenant(self.tenant).all()
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'

	class Meta:
		model=classstudent
		fields = ('class_section', 'roll_no','student', 'year',)
	def clean(self):
		cd= super(ClassStudentForm, self).clean()
		unique_class=cd.get('class_section')
		unique_year=cd.get('year')
		student=cd.get('student')
		error=[]
		data=""
		if not (unique_class or unique_year) :
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				class_selected=class_section.objects.for_tenant(self.tenant).get(name=unique_class)
				data=classstudent.objects.for_tenant(self.tenant).filter(year=unique_year).get(student=student)
				self.add_error('student',"Student for the same year already has a class.")
				self.add_error('year',"Student for the same year already has a class.")
			except:
				return cd
		return cd


#This for is to taking input of number of periods in class
class TotalPeriodForm(forms.ModelForm):
	class Meta:
		model=total_period
		fields = ('number_period',)
	def __init__(self, *args, **kwargs):
		self.tenant=kwargs.pop('tenant',None)
		super(TotalPeriodForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Submit', css_class="btn-xs"))
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-sm-2'
		self.helper.field_class = 'col-sm-4'
	def clean(self):
		cd= super(TotalPeriodForm, self).clean()
		unique_number=cd.get('number_period')
		error=[]
		data=""
		if not unique_number:
			raise forms.ValidationError(error)
			return cd
		else:
			try:
				data=total_period.objects.get(tenant=self.tenant)
				self.add_error('number_period',"Total number of periods already entered.")
			except:
				return cd
		return cd
