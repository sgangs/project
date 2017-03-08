from datetime import date, datetime
from dateutil.rrule import *
from dateutil.parser import *
from django.utils.timezone import localtime
from school_user.models import User, Tenant
from .models import annual_holiday_rules


def holiday_calculator(start, end, events, hol):
    rules=annual_holiday_rules.objects.all()
    for rule in rules:
        week_in_rule=list(map(int,str(rule.week)))
        x=list(rrule(MONTHLY, byweekday=(rule.day), bysetpos=(week_in_rule), dtstart=start,until=end))
        hol=hol+x
    events_work=events.filter(attendance_type=1)
    work=[]
    for event in events_work:
        work.append(datetime.strptime(datetime.strftime(localtime(event.date),'%Y %m %d'), '%Y %m %d'))
    hol=list(set(hol)-set(work))
    return hol

