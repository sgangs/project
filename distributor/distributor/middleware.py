from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

class CustomAuthenticationFailMaiddleware(MiddlewareMixin):

	# def process_exception(self, request, exception):
	# 	msg = None
	# 	print("Exception start: ")
	# 	print(exception)
	# 	print("Exception End")
	# 	# if (isinstance(exception, AuthFailed) and 
	# 	# 	exception.message == u"User not allowed"):
	# 	# 	msg =   u"Not in whitelist"
	# 	# else:
	# 	# 	msg =   u"Some other problem"

	# 	# messages.add_message(request, messages.ERROR, msg)
		# if (isinstance(exception, AuthenticationFailed)):
		# 	return HttpResponse("Oops payup dude")

	def process_response(self, request, response):
		# if (isinstance(exception, AuthFailed) and 
		# 	exception.message == u"User not allowed"):
		# 	msg =   u"Not in whitelist"
		# else:
		# 	msg =   u"Some other problem"

		# messages.add_message(request, messages.ERROR, msg)
		print(response)
		if (response.status_code == 401):
			print('here inside if')
			return HttpResponse("Payment is Due")
		else:
			print('outside if')
			return response