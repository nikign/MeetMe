import pytz

from django.utils import timezone

class TimezoneMiddleware(object):
	def process_request(self, request):
		tzname = request.session.get('django_timezone')
		if tzname:
			timezone.activate(pytz.timezone(tzname))
			# request.session['besar']=tzname
		else:
			timezone.activate(pytz.timezone('Asia/Tehran')) #TODO : fix
			# timezone.deactivate()
			# request.session['besar']='jafar'