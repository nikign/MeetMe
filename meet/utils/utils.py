from django.utils import timezone
from meet.utils import i18n
import pytz,datetime

def to_jalali(date_and_time=None, date=None, time=None, year=None, month=None, day=None, hour=0, minute=0, second=0):
	if date_and_time:
		time = date_and_time.time()
		date = date_and_time.date()
	else:
		time = time or datetime.time(hour,minute,second)
		date = date or datetime.date(year,month,day)
	return datetime.datetime.combine(i18n.tojalalidate(date),time)

def to_gregorian(date_and_time=None, date=None, time=None, year=None, month=None, day=None, hour=0, minute=0, second=0):
	if date_and_time:
		time = date_and_time.time()
		date = date_and_time.date()
	else:
		time = time or datetime.time(hour,minute,second)
		date = date or datetime.date(year,month,day)
	return datetime.datetime.combine(i18n.persiandate(date.year, date.month, date.day),time)

def to_local(date_and_time=None, date=None, time=None, year=None, month=None, day=None, hour=0, minute=0, second=0):
	if date_and_time:
		time = date_and_time.time()
		date = date_and_time.date()
	else:
		time = time or datetime.time(hour,minute,second)
		date = date or datetime.date(year,month,day)
	utc = pytz.UTC
	return utc.localize(datetime.datetime(date.year, date.month, date.day, time.hour, time.minute))

def has_passed(date_and_time=None, date=None, time=None, year=None, month=None, day=None, hour=0, minute=0, second=0, is_jalali=False):
	if date_and_time:
		time = date_and_time.time()
		date = date_and_time.date()
	else:
		time = time or datetime.time(hour,minute,second)
		date = date or datetime.date(year,month,day)
	if is_jalali:
		date = to_gregorian(date=date).date()
	utc = pytz.UTC
	now= utc.localize(datetime.datetime(date.year, date.month, date.day, time.hour, time.minute, time.second))
	return now< timezone.now()


def localdata(interval):
	localstart = to_local(date=interval.date, time=interval.start)
	localfinish = to_local(date=interval.date, time=interval.finish)
	return {'date':localstart.date(), 'start':localstart.time(), 'finish':localfinish.time()}

def jnow():
	gregorian_datetime = timezone.localtime(timezone.now())
	gregorian_date = gregorian_datetime.date()
	time = gregorian_datetime.time()
	return to_jalali(date=gregorian_date, time = time)


