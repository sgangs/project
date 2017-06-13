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
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate, Frame, Image
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Line




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

    def report(self, request):
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
        # year=int(request.POST.get('year'))
        # acad_year=academic_year.objects.for_tenant(this_tenant).get(year=year)
        # acad_year_start=acad_year.start
        # acad_year_end=acad_year.end
        data.append(Paragraph(" ", styles['Justify']))
        # for rd in response_data:
        #     if (rd['data_type'] == 'Student'):
        #         data.append(Paragraph('Name: '+rd['name'], styles['Justify'],))
        #         data.append(Paragraph('Class: '+rd['class_selected'], styles['Justify'],))
        #         data.append(Paragraph('Payment For Academic Year: '+acad_year_start.strftime('%b %d, %Y')\
        #                         +" to "+acad_year_end.strftime('%b %d, %Y'), styles['Justify'],))
        # insert a blank space
        data.append(Spacer(1, 12))
        total_fees_paid=0.00
        # for rd_outer in response_data:
        #     if (rd_outer['data_type'] == 'Month'):
        #         current_month=rd_outer['month']
        #         table_data = []
        #         data.append(Paragraph("Fee for the month of: " + current_month, styles['Justify']))
        #         data.append(Paragraph(" ", styles['Justify']))
        #         # table header
        #         table_data.append([Paragraph('Fee Structure', styles['TableHeader']), Paragraph('Amount', styles['TableHeader'])])
        #         total=0.00
        #         for rd in response_data:
        #             if (rd['data_type'] == 'Generic'):
        #                 if (rd['month_full'] == current_month):
        #                     # data.append(Paragraph(wh.observations, styles['Justify']))
        #                     # data.append(Spacer(1, 24))
        #                     # add a row to table
        #                     table_data.append(
        #                         [Paragraph(rd['name'], styles['TableData']),
        #                         Paragraph(rd['amount'], styles['TableData'])])
        #                     total+=float(rd['amount'])
        #                     total_fees_paid+=float(rd['amount'])
                            
                            
        #             if (rd['data_type'] == 'Late Fee'):
        #                 if (rd['month_full'] == current_month):
        #                     # data.append(Paragraph(wh.observations, styles['Justify']))
        #                     # data.append(Spacer(1, 24))
        #                     # add a row to table
        #                     table_data.append(
        #                         [Paragraph(rd['name'], styles['TableData']),
        #                         Paragraph(rd['amount'], styles['TableData'])])
        #                     total+=float(rd['amount'])
        #                     total_fees_paid+=float(rd['amount'])
        #                     table_data.append([Paragraph('Total Fees:', styles['TableHeader']),\
        #                                         Paragraph(str(total), styles['TableHeader'])])
        #                     # # create table                            
        #         table_data.append([Paragraph('Total Fees:', styles['TableHeader']),\
        #             Paragraph(str(total), styles['TableHeader'])])
        #         # create table
        #         fee_table = Table(table_data, colWidths=[doc.width/2.0]*2)
        #         fee_table.hAlign = 'LEFT'
        #         fee_table.setStyle(TableStyle(
        #             [('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        #             ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        #             ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        #             ('BACKGROUND', (0, 0), (-1, 0), colors.gray)]))
        #         data.append(fee_table)
        #         data.append(Spacer(1, 48))
        # details=[['Total Amount Paid: ', 'Rs. '+str(format(total_fees_paid, '.2f')), '(in words - Rupees '+\
                    # num2words(total_fees_paid,lang='en_IN').title()+' only)'],['Paid On: ', paid_on.strftime('%b %d, %Y')]]
        # payment=Table(details, hAlign='LEFT')
        # data.append (payment)
        doc.build(data, onFirstPage=self.pageNumber, onLaterPages=self.pageNumber)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        return pdf