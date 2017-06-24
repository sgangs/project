from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate


from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse



class MyBarcodeDrawing(Drawing):
    def __init__(self, text_value, *args, **kw):
        barcode = createBarcodeDrawing('Code128', value=text_value,  barHeight=20*mm, barWidth=0.3*mm, humanReadable=True)
        Drawing.__init__(self,barcode.width,barcode.height,*args,**kw)       
        self.add(barcode, name='barcode')
        

if __name__=='__main__':
    #use the standard 'save' method to save barcode.gif, barcode.pdf etc
    #for quick feedback while working.
    MyBarcodeDrawing("HELLO WORLD").save(formats=['gif','pdf'],outDir='.',fnRoot='barcode')




def write_pdf_view(request, pk_detail):
	try:
		this_tenant=request.user.tenant
		barcode=Product.objects.for_tenant(this_tenant).get(id=pk_detail).barcode
	    response = HttpResponse(content_type='application/pdf')
	    response['Content-Disposition'] = 'inline; filename="mypdf.pdf"'

	    buffer = BytesIO()
	    p = canvas.Canvas(buffer)

	    # Start writing the PDF here
	    p.drawString(100, 100, 'Hello world.')
	    # End writing

	    p.showPage()
	    p.save()

	    pdf = buffer.getvalue()
	    buffer.close()
	    response.write(pdf)

	    print(response)

    	return response