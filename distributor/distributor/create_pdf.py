from datetime import datetime


from django.utils.translation import ugettext_lazy as _
from reportlab.graphics.widgets.markers import makeMarker
#from reportlab.graphics.charts.barcharts import VerticalBarChart
#from reportlab.graphics.charts.legends import Legend
#from reportlab.graphics.charts.linecharts import SampleHorizontalLineChart
#from reportlab.graphics.charts.piecharts import Pie
#from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table,\
    TableStyle

from distribution_user.models import User, Tenant
from distribution_accounts.models import accountChart, journalGroup 
from distribution_master.models import Dimension, Unit
 

class PdfPrint:
	# initialize class
    def __init__(self, buffer, pageSize='A4'):
        self.buffer = buffer
        # default format is A4
        if pageSize == 'A4':
            self.pageSize = A4
        elif pageSize == 'Letter':
            self.pageSize = letter
        self.width, self.height = self.pageSize
