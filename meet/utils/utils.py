from django.utils import timezone
from meet.utils import i18n
import pytz,datetime

def to_jalali(date_and_time=None, date=None, time=None, year=None, month=None, day=None, hour=0, minute=0, second=0):
	utc = pytz.UTC
	if date_and_time:
		time = date_and_time.time()
		date = date_and_time.date()
	else:
		time = time or datetime.time(hour,minute,second)
		date = date or datetime.date(year,month,day)
	return datetime.datetime.combine(i18n.tojalalidate(date),time)

# def to_local(datetime=None, date=None, time=None, year=None, month=None, day=None, hour=0, minute=0, second=0):



def jdata(interval):
	start = utc.localize(datetime.datetime(interval.date.year, interval.date.month, interval.date.day, interval.start.hour, interval.start.minute)) 
	finish = utc.localize(datetime.datetime(interval.date.year, interval.date.month, interval.date.day, interval.finish.hour, interval.finish.minute))
	localstart = timezone.localtime(start)
	localfinish = timezone.localtime(finish)
	return {'date':localstart.date(), 'start':localstart.time(), 'finish':localfinish.time()}

def jnow():
	gregorian_datetime = timezone.localtime(timezone.now())
	gregorian_date = gregorian_datetime.date()
	time = gregorian_datetime.time()
	return to_jalali(date=gregorian_date, time = time)


