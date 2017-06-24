from decimal import Decimal
import datetime
import json
import os
import time
from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone
# from django.utils.timezone import localtime
from num2words import num2words
from dateutil.rrule import rrule, MONTHLY
from dateutil import parser
from time import strptime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A6, A5, A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate, Frame, Image
from reportlab.graphics.shapes import Line

from school.settings.base import STATIC_ROOT
from school_user.models import Tenant
from school_account.models import Account, Journal, journal_entry, journal_group, account_year, accounting_period
from school_eduadmin.models import class_section, classstudent
# from school_fees.models import student_fee, student_fee_payment
from school_student.models import Student
from school_genadmin.models import class_group, academic_year
from school_eduadmin.models import class_section, classstudent
# from .models import monthly_fee, monthly_fee_list, yearly_fee, yearly_fee_list
from .models import *
from school.school_general import *

def create_fee_structure(request, fee_type):
    with transaction.atomic():
        try:
            total=0
            month_data=[]
            this_tenant=request.user.tenant
            feename=request.POST.get('feename')
            fee_lists = json.loads(request.POST.get('details'))
            fee_create=generic_fee()
            month_all=json.loads(request.POST.get('month_all'))
            for item in month_all:
                month_data.append(item)
            fee_create.month=month_data
            fee_create.name=feename
            fee_create.tenant=this_tenant
            fee_create.save()
            for data in fee_lists:
                accountid=decoder(data['account'])[0]
                amount=float(data['amount'])
                name_fee_head=data['name']
                
                account=Account.objects.for_tenant(this_tenant).get(id=accountid)
                if name_fee_head =='':
                    name_fee_head=account.name
                fee_list=generic_fee_list()
                fee_list.generic_fee=fee_create
                fee_list.account = account
                fee_list.name = name_fee_head
                fee_list.amount= amount
                total+=amount
                fee_list.tenant=this_tenant
                fee_list.save()
            fee_create.total=total
            fee_create.save()
        except:
            transaction.rollback()

def view_fee_details(request):
    month_full={'Jan': 'January', 'Feb':'February', 'Mar':'March', 'Apr': 'April','May':'May','Jun':'June',\
                'Jul':'July', 'Aug':'August','Sep':'September', 'Oct':'October','Nov':'November','Dec':'December'}
    response_data=[]
    this_tenant=request.user.tenant
    studentid=request.POST.get('studentid')
    year=int(request.POST.get('year'))
    month=request.POST.get('month')
    class_input=request.POST.get('class_selected')
    class_selected=class_section.objects.for_tenant(request.user.tenant).get(id=class_input)
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    feelist=student_fee.objects.filter(student=student).get(year=year)
    response_data.append({'data_type':'Student','name':student.first_name+" "+student.last_name,'class_selected':class_selected.name})
    current_time=datetime.datetime.now()
    current_original=current_time
    acad_year=academic_year.objects.for_tenant(this_tenant).get(year=year)
    start_date=acad_year.start
    end_date=acad_year.end
    start=datetime.datetime.combine(start_date,datetime.datetime.min.time())
    start_month=start.month
    start_year=start.year
    end=datetime.datetime.combine(end_date,datetime.datetime.min.time())
    if (current_time>end):
        current_time=end
    all_months=[dt.strftime("%b") for dt in rrule(MONTHLY, dtstart=start, until=current_time)]
    months_paid=[]
    try:
        paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year)
        for item in paid:
            months_paid.append(item.month)
    except:
        pass
    pending_months=[x for x in all_months if x not in months_paid]
    try:
        late_fee_generic=late_fee_calculation.objects.get(tenant=this_tenant)
        last_day=late_fee_calculation.last_payment_date
        late_name=late_fee_calculation.name
    except:
        last_day=0
    for month in pending_months:
        is_month=False
        genericfeedetails=feelist.generic_fee.filter(month__contains=[month]).all()
        for genericfee in genericfeedetails:
            is_month=True
            genericfeelist=generic_fee_list.objects.filter(generic_fee=genericfee)
            for fee in genericfeelist:
                response_data.append({'data_type':'Generic','id':fee.id,'name':fee.name,\
                'amount':str(fee.amount), 'month_short':month, 'month_full':month_full[month]}) 
        if (is_month):
            if (last_day>0):
                cur_month=int((strptime(month, '%b').tm_mon))
                try:
                    if (cur_month<start_month):
                        date_str=str(format(last_day,"02d")+"-"+format(cur_month,"02d")+"-"+str(year+1)+"-"+"00:00:00")
                    else:
                        date_str=str(format(last_day,"02d")+"-"+format(cur_month,"02d")+"-"+str(year)+"-"+"00:00:00")
                    last_date=parser.parse(date_str)
                    delay=current_original-last_date
                    if (delay>0):
                        try:
                            late_fee_amount=late_fee_slab.objects.filter(late_fee=late_fee_generic, last_slab=False,\
                                days_after_due__gte=delay).order_by('days_after_due').first().amount
                        except:
                            slab_selected=late_fee_slab.objects.get(late_fee=late_fee_generic, last_slab=True)
                        response_data.append({'data_type':'Late Fee','name':late_name.name,'amount':str(slab_selected.amount),\
                        'id':slab_selected.id,'month_short':month, 'month_full':month_full[month]}) 
                except:
                    pass

            response_data.append({'data_type':'Month','month':month_full[month]})
    return response_data




def view_payment_details (request):
    this_tenant=request.user.tenant
    response_data = []
    studentid=request.POST.get('studentid')
    year=int(request.POST.get('year'))
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    fee_paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year)
    for fee in fee_paid:
        print(fee.paid_on.isoformat())
        response_data.append({'data_type':'payment','month':fee.month, 'amount':str(fee.amount),'paid_on':fee.paid_on.isoformat()})
    return response_data


def view_student_fees(request):
    response_data=[]
    this_tenant=request.user.tenant
    studentid=request.POST.get('student_id')
    year=int(request.POST.get('year'))
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    feelist=student_fee.objects.filter(student=student).get(year=year)
    for genericfee in feelist.generic_fee.all():
        genericfeelist=generic_fee_list.objects.filter(generic_fee=genericfee)
        for fee in genericfeelist:
            response_data.append({'data_type':'Generic','id':fee.id,'name':fee.name, 'account':fee.account.id,\
            'amount':str(fee.amount)})    
    return response_data

def view_class_fees(request):
    response_data=[]
    this_tenant=request.user.tenant
    try:
        year=int(request.POST.get('year'))
    except:
        year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
    classid=request.POST.get('class_selected')
    class_selected=class_section.objects.for_tenant(this_tenant).get(id=classid)
    feelist=group_default_fee.objects.for_tenant(this_tenant).get(year=year, classgroup=class_selected.classgroup)
    genericfeedetails=feelist.generic_fee.all()
    for genericfee in genericfeedetails:
        genericfeelist=generic_fee_list.objects.filter(generic_fee=genericfee).all().select_related('generic_fee')
        for fee in genericfeelist:
            response_data.append({'data_type':'Generic','name':fee.name, 'month':fee.generic_fee.month,\
            'amount':str(fee.amount)})
    return response_data


def view_student(request):
    response_data = []
    this_tenant=request.user.tenant
    class_input=request.POST.get('class_selected')
    try:
        year=int(request.POST.get('year'))
    except:
        year=academic_year.objects.for_tenant(this_tenant).get(current_academic_year=True).year
    class_selected=class_section.objects.for_tenant(this_tenant).get(id=class_input)
    studentlist=classstudent.objects.filter(class_section=class_selected, year=year).select_related('student')
    for student in studentlist:
        response_data.append({'data_type':'Student','id':student.student.id,'first_name':student.student.first_name, \
            'last_name':student.student.last_name,'key':student.student.key,'local_id':student.student.local_id,})
    return response_data

def save_student_payment(request):
    month_short={'January': 'Jan', 'February':'Feb', 'March':'Mar', 'April': 'Apr','May':'May','June':'Jun',\
                'July':'Jul', 'August':'Aug','September':'Sep', 'October':'Oct','November':'Nov','December':'Dec'}
    this_tenant=request.user.tenant
    response_data = []
    studentid=int(request.POST.get('studentid'))
    year=int(request.POST.get('year'))
    amount=Decimal(int(request.POST.get('amount')))
    month_list=json.loads(request.POST.get('month_list'))
    student=Student.objects.for_tenant(this_tenant).get(id=studentid)
    student_classid = classstudent.objects.get(year=year, student=student).class_section.id
    class_selected = class_section.objects.get(id=student_classid)
    student_name=student.first_name + " " + student.last_name
    feelist=student_fee.objects.for_tenant(this_tenant).get(student=student,year=year)
    now=datetime.date.today()
    tz_unaware_now=datetime.datetime.strptime(str(now), "%Y-%m-%d")
    tz_aware_now=timezone.make_aware(tz_unaware_now, timezone.get_current_timezone())
    # amount_paid=0
    # fee_paid=0
    acct_period=accounting_period.objects.for_tenant(this_tenant).get(start__lte=now,end__gte=now)
    current_time=datetime.datetime.now()
    month_total=0
    with transaction.atomic():
        try:
            for month_full in month_list:
                month=month_short[month_full['month']]
                amount_paid=0
                # fee_paid=0
                genericfeedetails=feelist.generic_fee.filter(month__contains=[month]).all()
                # try:
                #     fee_paid=student_fee_payment.objects.for_tenant(this_tenant).filter(student=student,year=year,month=month)\
                #         .aggregate(Sum('amount'))        
                # except:
                #     pass
                fee_payment=student_fee_payment()
                fee_payment.student=student
                fee_payment.student_class=class_selected
                fee_payment.month=month
                fee_payment.year=year
                fee_payment.paid_on=tz_aware_now
                fee_payment.amount=amount_paid #Initially it is zero.
                fee_payment.tenant=this_tenant
                fee_payment.save()
                for genericfee in genericfeedetails:
                    genericfeelist=generic_fee_list.objects.filter(generic_fee=genericfee)
                    for fee in genericfeelist:
                        account=Account.objects.for_tenant(this_tenant).get(id=fee.account.id)
                        this_amount=fee.amount
                        amount_paid+=this_amount
                        month_total+=this_amount
                        new_journal_entry(account,this_amount,this_tenant,student_name, tz_aware_now, acct_period)
                        lineitem=payment_line_item()
                        lineitem.fee_payment=fee_payment
                        lineitem.name=fee.name
                        lineitem.amount=fee.amount
                        lineitem.tenant=this_tenant
                        lineitem.save()
                if month_full['is_late'] =="Yes":
                    late_slab=late_fee_slab.objects.for_tenant(this_tenant).get(id=month_full['slab'])
                    late_fee_rule=late_fee_calculation.objects.get(tenant=this_tenant)
                    account=Account.objects.for_tenant(this_tenant).get(lateFeeCalculation_fees_account_account=fee.account.id)
                    this_amount=late_slab.amount
                    amount_paid+=this_amount
                    month_total+=this_amount
                    new_journal_entry(account,this_amount,this_tenant,student_name, tz_aware_now, acct_period)
                    lineitem=payment_line_item()
                    lineitem.fee_payment=fee_payment
                    lineitem.name=late_fee_rule.name
                    lineitem.amount=late_slab.amount
                    lineitem.tenant=this_tenant
                    lineitem.save()
                    new_late_fee= student_late_fee()
                    new_late_fee.student=student
                    new_late_fee.month=month
                    new_late_fee.year=year
                    new_late_fee.paid_on=tz_aware_now
                    new_late_fee.student_class=class_selected
                    new_late_fee.name=late_fee_rule.name
                    new_late_fee.amount=late_slab.amount
                    new_late_fee.tenant=this_tenant
                    new_late_fee.save() 
                # if (amount_paid != amount):
                #     raise IntegrityError
                #     transaction.rollback()
                # if (amount == fee_paid):
                #     raise IntegrityError
                #     transaction.rollback()
                fee_payment.amount=amount_paid   
                fee_payment.save()
            if (month_total != amount):
                raise IntegrityError
                transaction.rollback()
        except:
            transaction.rollback()
    return tz_aware_now

def new_journal_entry(account, amount, this_tenant,name,tz_aware_now, acct_period):
    journal=Journal()
    journal.date=tz_aware_now
    group=journal_group.objects.for_tenant(this_tenant).get(name="General")
    journal.group=group
    journal.remarks="Fees for: "+name
    journal.tenant=this_tenant
    journal.save()
    account=account
    # This line has to change to accomodate acct. period according to current date.
    # acct_period=accounting_period.objects.for_tenant(this_tenant).get(current_period=True)
    i=1
    while (i<3):
        entry=journal_entry()
        entry.journal=journal
        if (i==1):
            entry.account=account
            entry.transaction_type="Credit"
            account_journal_year=account_year.objects.get(account=account, accounting_period = acct_period)
            account_journal_year.current_credit=account_journal_year.current_credit+amount
            account_journal_year.save()
            account.save()
        else:
            account=Account.objects.for_tenant(this_tenant).get(key='cash')
            entry.account=account
            account_journal_year=account_year.objects.get(account=account, accounting_period = acct_period)
            account_journal_year.current_debit=account_journal_year.current_debit+amount
            account_journal_year.save()
            account.save()
            entry.transaction_type="Debit"
        entry.value=amount
        entry.tenant=this_tenant
        entry.save()
        i+=1


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
        footer="Generated on: "+timestring
        # stamp_paid = Image(os.path.join(settings.STATIC_ROOT, 'img/stamp_paid.jpg'))
        # print(stamp_paid)
        canvas.drawCentredString(100*mm, 15*mm, str(number))
        canvas.drawCentredString(50*mm, 15*mm, str(footer))
        # canvas.drawCentredString(100 * mm, 100 * mm, stamp_paid)    

    def report(self, request, paid_on, response_data, title):
        doc = SimpleDocTemplate(self.buffer,rightMargin=72,leftMargin=72,topMargin=30,bottomMargin=72,pagesize=self.pageSize)
        styles = getSampleStyleSheet()
        styles.wordWrap = 'CJK'
        styles.add(ParagraphStyle(name="TableHeader", fontSize=11, alignment=TA_CENTER))        
        styles.add(ParagraphStyle(name="Small", fontSize=8, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name="TableData", fontSize=9, alignment=TA_CENTER))
        styles.add(ParagraphStyle(name='Justify', fontSize=10, alignment=TA_JUSTIFY, leading=20))
        styles.add(ParagraphStyle(name='Summary', fontSize=10, alignment=TA_JUSTIFY, \
            leading=20, borderPadding = 25,backColor=colors.gray ))
        # list used for elements added into document
        data = []
        this_tenant=request.user.tenant
        data.append(Paragraph(this_tenant.name, styles['Title']))
        data.append(Paragraph(this_tenant.address, styles['Small']))
        line_data=[" "]
        line_table = Table(line_data, colWidths=doc.width)        
        line_table.setStyle(TableStyle([("LINEBELOW", (0,0), (-1,-1), 1, colors.black)]))
        data.append(line_table)
        year=int(request.POST.get('year'))
        acad_year=academic_year.objects.for_tenant(this_tenant).get(year=year)
        acad_year_start=acad_year.start
        acad_year_end=acad_year.end
        data.append(Paragraph(" ", styles['Justify']))
        for rd in response_data:
            if (rd['data_type'] == 'Student'):
                data.append(Paragraph('Name: '+rd['name'], styles['Justify'],))
                data.append(Paragraph('Class: '+rd['class_selected'], styles['Justify'],))
                data.append(Paragraph('Payment For Academic Year: '+acad_year_start.strftime('%b %d, %Y')\
                                +" to "+acad_year_end.strftime('%b %d, %Y'), styles['Justify'],))
        # insert a blank space
        data.append(Spacer(1, 12))
        total_fees_paid=0.00
        for rd_outer in response_data:
            if (rd_outer['data_type'] == 'Month'):
                current_month=rd_outer['month']
                table_data = []
                data.append(Paragraph("Fee for the month of: " + current_month, styles['Justify']))
                data.append(Paragraph(" ", styles['Justify']))
                # table header
                table_data.append([Paragraph('Fee Structure', styles['TableHeader']), Paragraph('Amount', styles['TableHeader'])])
                total=0.00
                for rd in response_data:
                    if (rd['data_type'] == 'Generic'):
                        if (rd['month_full'] == current_month):
                            # data.append(Paragraph(wh.observations, styles['Justify']))
                            # data.append(Spacer(1, 24))
                            # add a row to table
                            table_data.append(
                                [Paragraph(rd['name'], styles['TableData']),
                                Paragraph(rd['amount'], styles['TableData'])])
                            total+=float(rd['amount'])
                            total_fees_paid+=float(rd['amount'])
                            
                            
                    if (rd['data_type'] == 'Late Fee'):
                        if (rd['month_full'] == current_month):
                            # data.append(Paragraph(wh.observations, styles['Justify']))
                            # data.append(Spacer(1, 24))
                            # add a row to table
                            table_data.append(
                                [Paragraph(rd['name'], styles['TableData']),
                                Paragraph(rd['amount'], styles['TableData'])])
                            total+=float(rd['amount'])
                            total_fees_paid+=float(rd['amount'])
                            table_data.append([Paragraph('Total Fees:', styles['TableHeader']),\
                                                Paragraph(str(total), styles['TableHeader'])])
                            # # create table                            
                table_data.append([Paragraph('Total Fees:', styles['TableHeader']),\
                    Paragraph(str(total), styles['TableHeader'])])
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
        details=[['Total Amount Paid: ', 'Rs. '+str(format(total_fees_paid, '.2f')), '(in words - Rupees '+\
                    num2words(total_fees_paid,lang='en_IN').title()+' only)'],['Paid On: ', paid_on.strftime('%b %d, %Y')]]
        payment=Table(details, hAlign='LEFT')
        data.append (payment)
        doc.build(data, onFirstPage=self.pageNumber, onLaterPages=self.pageNumber)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf