from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder


def paginate_data(page_no, total_per_page, objects):
	response_data={}
	paginator = Paginator(objects, total_per_page)
	object_paginated=paginator.page(page_no)
			
	objects_list=objects[(int(page_no)-1)*total_per_page:int(page_no)*total_per_page]
	index = paginator.page_range.index(object_paginated.number)
	max_index = len(paginator.page_range)
	start_index = index - 3 if index >= 3 else 0

	end_index = index + 3 if index <= max_index - 3 else max_index
		
	response_data['object']=objects_list
	response_data['start']=start_index
	response_data['end']=end_index
	# response_data['has_previous']=paginator.has_previous()
	# response_data['has_next']=paginator.has_next()
	return response_data