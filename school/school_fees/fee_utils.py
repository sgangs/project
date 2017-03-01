from decimal import Decimal
import datetime
import json
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.timezone import localtime
from num2words import num2words

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A6, A5, A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate, Frame
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Line

from school.settings.base import STATIC_ROOT
from school_user.models import Tenant
from school_account.models import Account, Journal, journal_entry, journal_group
from school_eduadmin.models import class_section, classstudent
from school_fees.models import student_fee, student_fee_payment
from school_student.models import Student
from school_genadmin.models import class_group
from .models import monthly_fee, monthly_fee_list, yearly_fee, yearly_fee_list
from school.school_general import *

def create_fee_structure(request, fee_type):
    with transaction.atomic():
        try:
            this_tenant=request.user.tenant
            #create_fee_structure(request, fee_type)
            feename=request.POST.get('feename')
            fee_lists = json.loads(request.POST.get('details'))
            # months = json.loads(request.POST.get('months'))
            if (fee_type == 'Monthly'):
                fee_create=monthly_fee()
            else:
                fee_create=yearly_fee()
                month=request.POST.get('month')
                fee_create.month=month
            fee_create.name=feename
            fee_create.tenant=this_tenant
            fee_create.save()
            for data in fee_lists:
                accountid=decoder(data['account'])[0]
                amount=float(data['amount'])
                account=Account.objects.for_tenant(this_tenant).get(id=accountid)
                if (fee_type == 'Monthly'):
                    fee_list=monthly_fee_list()
                    fee_list.monthly_fee=fee_create
                else:
                    fee_list=yearly_fee_list()
                    fee_list.yearly_fee=fee_create
                fee_list.account = account
                fee_list.name = account.name
                fee_list.amount= amount                                   
                fee_list.tenant=this_tenant
                fee_list.save()
        except:
            transaction.rollback()


def view_fee_details(request):
    response_data=[]
    this_tenant=request.user.tenant
    studentid=request.POST.get('studentid')
    year=int(request.POST.get('year'))
    month=request.POST.get('month')
    class_input=request.POST.get('class_selected')
    class_selected=class_section.objects.for_tenant(request.user.tenant).get(id=class_input)
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    feelist=student_fee.objects.filter(student=student).get(year=year)
    monthlyfee=feelist.monthly_fee
    monthlyfeelist=monthly_fee_list.objects.filter(monthly_fee=monthlyfee)
    paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year,month=month).aggregate(Sum('amount'))
    try:
        yearlyfeedetails=feelist.yearly_fee.filter(month=month).all()
    except:
        yearlyfeedetails=''
    response_data.append({'data_type':'Student', 'name':student.first_name+" "+student.last_name, \
        'class_selected': class_selected.name})
    if (paid['amount__sum'] != None):
        if (paid['amount__sum'] > 0):
            response_data.append({'data_type':'Paid', 'amount':str(paid['amount__sum'])})
    for fee in monthlyfeelist:
        response_data.append({'data_type':'Monthly','id':fee.id,'name':fee.name, 'account':fee.account.id,\
            'amount':str(fee.amount)})
    try:
        for yearlyfee in yearlyfeedetails:
            yearlyfeelist=yearly_fee_list.objects.filter(yearly_fee=yearlyfee)
            for fee in yearlyfeelist:
                response_data.append({'data_type':'Yearly','id':fee.id,'name':fee.name, 'account':fee.account.id,\
                    'amount':str(fee.amount)})
    except:
        pass
    return response_data


def view_student(request):
    response_data = []
    class_input=request.POST.get('class_selected')
    year=int(request.POST.get('year'))
    class_selected=class_section.objects.for_tenant(request.user.tenant).get(id=class_input)
    group=class_selected.classgroup
    studentlist=classstudent.objects.filter(class_section=class_selected, year=year).select_related('student')
    for student in studentlist:
        response_data.append({'data_type':'Student','id':student.student.id,'first_name':student.student.first_name, \
            'last_name':student.student.last_name,'key':student.student.key,'local_id':student.student.local_id,})
    return response_data

def save_student_payment(request):
    this_tenant=request.user.tenant
    response_data = []
    studentid=request.POST.get('studentid')
    year=int(request.POST.get('year'))
    month=request.POST.get('month')
    amount=Decimal(int(request.POST.get('amount')))
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    student_name=student.first_name + " " + student.last_name
    feelist=student_fee.objects.for_tenant(this_tenant).get(student=student,year=year)
    monthlyfee=feelist.monthly_fee
    monthlyfeelist=monthly_fee_list.objects.filter(monthly_fee=monthlyfee)
    now=datetime.date.today()
    tz_unaware_now=datetime.datetime.strptime(str(now), "%Y-%m-%d")
    tz_aware_now=timezone.make_aware(tz_unaware_now, timezone.get_current_timezone())
    amount_paid=0
    fee_paid=0
    try:
        fee_paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year,month=month)\
            .aggregate(Sum('amount'))        
    except:
        pass
    try:
        yearlyfeedetails=feelist.yearly_fee.filter(month=month).all()
    except:
        yearlyfeedetails=''
    with transaction.atomic():
        try:
            for fee in monthlyfeelist:
                account=Account.objects.for_tenant(this_tenant).get(id=fee.account.id)
                this_amount=fee.amount
                amount_paid+=this_amount
                new_journal_entry(account,this_amount,this_tenant,student_name, tz_aware_now)
            for yearlyfee in yearlyfeedetails:
                yearlyfeelist=yearly_fee_list.objects.filter(yearly_fee=yearlyfee)
                for fee in yearlyfeelist:
                    account=Account.objects.for_tenant(this_tenant).get(id=fee.account.id)
                    this_amount=fee.amount
                    amount_paid+=this_amount
                    new_journal_entry(account,this_amount,this_tenant,student_name, tz_aware_now)
            if (amount_paid != amount):
                raise IntegrityError
                transaction.rollback()
            if (amount == fee_paid):
                raise IntegrityError
                transaction.rollback()
            fee_payment=student_fee_payment()
            fee_payment.student=student
            fee_payment.month=month
            fee_payment.year=year
            fee_payment.paid_on=tz_aware_now
            fee_payment.amount=amount_paid
            fee_payment.tenant=this_tenant
            fee_payment.save()
        except:
            transaction.rollback()
    return tz_aware_now



def new_journal_entry(account, amount, this_tenant,name,tz_aware_now):
    journal=Journal()
    journal.date=tz_aware_now
    group=journal_group.objects.for_tenant(this_tenant).get(name="General")
    journal.group=group
    journal.remarks="Fees for: "+name
    journal.tenant=this_tenant
    journal.save()
    account=account
    i=1
    while (i<3):
        entry=journal_entry()
        entry.journal=journal
        if (i==1):
            entry.account=account
            entry.transaction_type="Credit"
            account.current_credit=account.current_credit+amount
            account.save()
        else:
            account=Account.objects.for_tenant(this_tenant).get(key='cash')
            entry.account=account
            account.current_debit=account.current_debit+amount
            account.save()
            entry.transaction_type="Debit"
        entry.value=amount
        entry.tenant=this_tenant
        entry.save()
        i+=1

def view_payment_details (request):
    this_tenant=request.user.tenant
    response_data = []
    studentid=request.POST.get('studentid')
    year=int(request.POST.get('year'))
    print (year)
    # month=request.POST.get('month')
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    fee_paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year)
    print (fee_paid)
    for fee in fee_paid:
        response_data.append({'data_type':'payment','month':fee.month, 'amount':str(fee.amount),'paid_on':fee.paid_on.isoformat()})
    return response_data

# pdfmetrics.registerFont(TTFont('OpenSans-Regular', STATIC_ROOT + '/fonts/OpenSans-Regular.ttf'))
# pdfmetrics.registerFont(TTFont('OpenSans-Light', STATIC_ROOT + '/fonts/OpenSans-Light.ttf'))
# pdfmetrics.registerFont(TTFont('OpenSans-Bold', STATIC_ROOT + '/fonts/OpenSans-Bold.ttf'))

# pdfmetrics.registerFontFamily('FansyFont', normal='OpenSans-Regular', bold='OpenSans-Bold', italic='OpenSans-Light',)

class PdfPrint:
    def __init__(self, buffer, pageSize):
        self.buffer = buffer
        self.pageSize = A4
        self.width, self.height = self.pageSize

    def pageNumber(self, canvas, doc):
        number = canvas.getPageNumber()
        now=datetime.datetime.now()
        tz_aware_now=timezone.make_aware(now, timezone.get_current_timezone())
        timestring= tz_aware_now.strftime('%Y-%m-%d at %H:%M:%S hrs')
        footer="Printed on: "+timestring
        canvas.drawCentredString(100*mm, 15*mm, str(number))
        canvas.drawCentredString(50*mm, 15*mm, str(footer))

    

    def report(self, request, paid_on, response_data, title):
        doc = SimpleDocTemplate(self.buffer,rightMargin=72,leftMargin=72,topMargin=30,bottomMargin=72,pagesize=self.pageSize)
        # doc = SimpleDocTemplate(self.buffer,pagesize=self.pageSize)
        # a collection of styles offer by the library
        styles = getSampleStyleSheet()
        styles.wordWrap = 'CJK'
        # add custom paragraph style - The issue is with custom fonts
        # styles.add(ParagraphStyle(name="TableHeader", fontSize=11, alignment=TA_CENTER,fontName="OpenSans-Bold"))
        # styles.add(ParagraphStyle(name="ParagraphTitle", fontSize=14, alignment=TA_JUSTIFY,fontName="OpenSans-Bold"))
        # styles.add(ParagraphStyle(name="ParagraphName", fontSize=10, alignment=TA_JUSTIFY,fontName="OpenSans-Bold"))
        # styles.add(ParagraphStyle(name="Justify", alignment=TA_JUSTIFY, fontName="OpenSans-Regular"))
        styles.add(ParagraphStyle(name="TableHeader", fontSize=11, alignment=TA_CENTER))        
        styles.add(ParagraphStyle(name="Small", fontSize=8, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="TableData", fontSize=9, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='Justify', fontSize=10, alignment=TA_JUSTIFY, leading=20))
        styles.add(ParagraphStyle(name='Summary', fontSize=10, alignment=TA_JUSTIFY, \
            leading=20, borderPadding = 25,backColor=colors.gray ))
        # list used for elements added into document
        data = []
        data.append(Paragraph(request.user.tenant.name, styles['Title']))
        data.append(Paragraph(request.user.tenant.address, styles['Small']))
        line_data=[" "]
        line_table = Table(line_data, colWidths=doc.width)        
        line_table.setStyle(TableStyle([("LINEBELOW", (0,0), (-1,-1), 1, colors.black)]))
        data.append(line_table)
        year=int(request.POST.get('year'))
        month=request.POST.get('month')
        data.append(Paragraph("Fee for the month of: " + month+ ", Academic year (start): "+ str(year), \
                styles['Justify']))
        data.append(Paragraph(" ", styles['Justify']))
        for rd in response_data:
            if (rd['data_type'] == 'Student'):
                data.append(Paragraph('Name: '+rd['name'], styles['Justify'],))
                data.append(Paragraph('Class: '+rd['class_selected'], styles['Justify'],))
        # insert a blank space
        data.append(Spacer(1, 12))
        table_data = []

        # table header
        table_data.append([Paragraph('Fee Structure', styles['TableHeader']), Paragraph('Amount', styles['TableHeader'])])
        total=0.00
        for rd in response_data:
            if (rd['data_type'] == 'Monthly' or rd['data_type']=='Yearly'):
                # data.append(Paragraph(wh.observations, styles['Justify']))
                # data.append(Spacer(1, 24))
                # add a row to table
                table_data.append(
                    [Paragraph(rd['name'], styles['TableData']),
                    Paragraph(rd['amount'], styles['TableData'])])
                total+=float(rd['amount'])
        table_data.append([Paragraph('Total Fees:', styles['TableHeader']), Paragraph(str(total), styles['TableHeader'])])
        # create table
        fee_table = Table(table_data, colWidths=[doc.width/2.0]*2)
        fee_table.hAlign = 'LEFT'
        fee_table.setStyle(TableStyle(
            [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
             ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
             ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
             ('BACKGROUND', (0, 0), (-1, 0), colors.gray)]))
        data.append(fee_table)
        data.append(Spacer(1, 48))
        details=[['Amount Paid: ', 'Rs. '+str(format(total, '.2f')), '(in words - Rupees '+num2words(total,lang='en_IN').title() +')'],
                    ['Paid On: ', paid_on.strftime('%Y-%m-%d')]]
        payment=Table(details, hAlign='LEFT')
        data.append (payment)
        doc.build(data, onFirstPage=self.pageNumber, onLaterPages=self.pageNumber)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf