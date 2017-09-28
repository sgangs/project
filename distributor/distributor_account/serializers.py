from rest_framework import serializers
from .models import *

class PaymentModeSerializers (serializers.ModelSerializer):
	payment_account=serializers.StringRelatedField()
	class Meta:
		model = payment_mode
		fields = ('id','name','payment_account', 'default')

class LedgerGroupSerializers (serializers.ModelSerializer):
	# account=serializers.StringRelatedField()
	class Meta:
		model = ledger_group
		fields = ('id','name')

class JournalGroupSerializers (serializers.ModelSerializer):
	# account=serializers.StringRelatedField()
	class Meta:
		model = journal_group
		fields = ('id','name')

class AccountingPeriodSerializers (serializers.ModelSerializer):
	# payment_account=serializers.StringRelatedField()
	class Meta:
		model = accounting_period
		fields = ('id','start','end', 'current_period', 'finalized', 'is_first_year')

# class AccountYearSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = account_year
#         fields = ('opening_debit', 'opening_credit', 'current_debit','current_credit', 'closing_debit', 'closing_credit')

# class AccountSerializer(serializers.ModelSerializer):
#     accountYear_account = AccountYearSerializer(many=True)

#     class Meta:
#         model = Account
#         fields = ('id', 'name', 'remarks','account_type', 'accountYear_account')


