state_list=(('35','Andaman & Nicobar Island'),
			('28','Andhra Pradesh'),
			('12','Arunachal Pradesh'),
			('18','Assam'),
			('10','Bihar'),
			('04','Chandigarh'),
			('22','Chattisgarh'),
			('26','Dadra & Nagar Haveli'),
			('25','Daman & Diu'),
			('07','National Capital Territory of Delhi'),
			('30','Goa'),
			('24','Gujrat'),
			('06','Haryana'),
			('02','Himachal Pradesh'),
			('01','Jammu & Kashmir'),
			('20','Jharkhand'),
			('29','Karnataka'),
			('32','Kerala'),
			('31','Lakshadweep'),
			('23','Madhya Pradesh'),
			('27','Maharashtra'),
			('14','Manipur'),
			('17','Meghalaya'),
			('15','Mizoram'),
			('13','Nagaland'),
			('21','Odisha'),
			('34','Puducherry'),
			('03','Punjab'),
			('08','Rajashtan'),
			('11','Sikkim'),
			('33','Tamil Nadu'),
			('TEL','Telengana'),
			('16','Tripura'),
			('09','Uttar Pradesh'),
			('UTT','Uttarkhand'),
			('05','Uttarkhand'),
			('19','West Bengal'),)

account=(('Basic','Basic'),
			('SMS_Active','SMS_Active'))

tenant_type=((1,'Distributor'),
			(2,'Retailer'),
			(3,'Both Retail & Distributor'))

user_type=(('Owner','Owner'),
			('Salesperson','Salesperson'),)


#Add user permission.

discount_type_options=((1,'Value'),
			(2,'Percentage'))


#Inventory Changes Here.
transaction_choices=((1,'Purchase'), #Inventory Increase
			(2,'Sales'), #Inventory Decrease
			(3,'Sales Return'), #Inventory Increase
			(4,'Other Inward'), #Inventory Increase
			(5,'Purchase Return'), #Inventory Decrease
			(6,'Other Outward'), #Inventory Decrease
			(7,'Transfer Outward'), #Inventory Decrease
			(8,'Transfer Inward'), #Inventory Increase
			(9,'Retail Sales'), #Inventory Decrease
			(9,'Retail Sales Return'),) #Inventory Increase
 

#transaction_choices option 1 also includes first time inventory

account_type_general=(('ca','Current Assets'),
				('rec','Receivable/Sundry Debtors'), #This is an asset account
				('nca','Non Current/Long Term Assets'),
				('cl','Current Liabilities'),
				('pay','Payables/Sundry Creditors'), #This is a liability account
				('ncl','Non Current/Long Term Liabilities'),
				# ('O','Owner'),
				('dirrev','Direct Revenue'),
				('indrev','Indirect Revenue'),
				('direxp','Direct Expense'),
				('indexp','Indirect Expense'),
				('taxexp','Tax Expense'),
				('equ','Equity/Owner/Capital'),)

activity_type_choces=((1,'Operating Activity'),
			(2,'Investing Activity'),
			(3,'Financing Activity'))


gst_invoice_type=((1,'B2BR'), #B2B Registered
			(2,'B2BUR'), #B2B Unregistered
			(3,'B2BRA'), #B2B Registered Amendmend
			(4,'B2BURA'), #B2B Unregistered Amendmend
			(5,'B2BIN'), #B2B Interstate
			(6,'B2BINA'), #B2B Interstate Amendment
			(7,'B2CL'), #B2C Large
			(8,'B2CS'), #B2C Small
			(9,'B2BSSUPD'), #B2B Supplementary Debit Note
			(10,'B2BSSUPC'), #B2B Supplementary Credit Note
			(11,'B2CSSUPD'), #B2C Supplementary Debit Note
			(12,'B2CSSUPC'),) #B2C Supplementary Credit Note