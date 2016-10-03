from django import template

register = template.Library()

@register.simple_tag
def subtract_tag(val1, val2):
	result=val1-val2
	return result