from django.utils import timezone
from meet.utils import i18n

import pytz,datetime

def jdata(interval):
	utc = pytz.UTC
	start = utc.localize(datetime.datetime(interval.date.year, interval.date.month, interval.date.day, interval.start.hour, interval.start.minute)) 
	finish = utc.localize(datetime.datetime(interval.date.year, interval.date.month, interval.date.day, interval.finish.hour, interval.finish.minute))
	localstart = timezone.localtime(start)
	localfinish = timezone.localtime(finish)
	return {'date':localstart.date(), 'start':localstart.time(), 'finish':localfinish.time()}

def jnow():
	return timezone.localtime(timezone.now())
	

