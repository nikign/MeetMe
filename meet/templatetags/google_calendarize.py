from django import template
from django.contrib.sites.models import Site
from django.utils.http import urlquote_plus
import datetime

register = template.Library()

@register.filter
def google_calendarize(event):
    st = event.reservation.interval.start
    en = event.reservation.interval.finish
    date = event.reservation.interval.date
    st = datetime.datetime.combine(date, st)
    en = datetime.datetime.combine(date, en)
    tfmt = '%Y%m%dT000000'

    dates = '%s%s%s' % (st.strftime(tfmt), '%2F', en.strftime(tfmt))
    name = urlquote_plus(event.title)

    s = ('http://www.google.com/calendar/event?action=TEMPLATE&' +
         'text=' + name + '&' +
         'dates=' + dates + '&' +
         'sprop=website:' + urlquote_plus(Site.objects.get_current().domain))

    if event.reservation.room.address:
        s = s + '&location=' + urlquote_plus(event.reservation.room.address)

    return s + '&trp=false'

google_calendarize.safe = True