from django import template
from meet.utils import i18n
from meet.utils.utils import localdata
from django.contrib.sites.models import Site
from django.utils.http import urlquote_plus
import datetime
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter
def google_calendarize(event):
    st = event.reservation.interval.start
    en = event.reservation.interval.finish
    date = event.reservation.interval.date
    st = datetime.datetime.combine(date, st)
    en = datetime.datetime.combine(date, en)
    tfmt = '%Y%m%dT%H%M%S'

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

@register.filter
def jdate(value, lang=None):
    """
    Converts a date to unicode 'year/month/day'
    """
    if not value:
        return mark_safe('&mdash;')
    lang = lang or translation.get_language()
    if isinstance(value, datetime.datetime):
        # if local_tz:
        #     timezone = getattr(value, 'tzinfo', None)
        #     if timezone:
        #         value = value.astimezone(local_tz)
        value = value.date()
    if lang == 'en':
        return "%d/%d/%d" % (value.year, value.month, value.day)
    d = i18n.topersiandate(value)
    return i18n.iranian_digits("%d %s %d" % (d[2], d[1], d[0]))


@register.filter
def jdate_day(value, lang=None):
    """
    Converts a date to unicode 'day'
    """
    res = jdate(value, lang)
    return res.split()[0]

@register.filter
def len_literal(value, lang=None):
    l = len(value)
    lang = lang or translation.get_language()
    if lang == 'en':
        return "%d" % l
    return i18n.to_literal(l, lang)    


@register.filter
def jtime(value, lang=None):
    if not value:
        return ""
    lang = lang or translation.get_language()
    # TODO: value.astimezone(local_tz)
    result = "%02d:%02d" % (value.hour, value.minute)
    if lang == 'fa':
        result = i18n.iranian_digits(result)
    return result


@register.filter
def jdatetime(value, lang=None):
    return jdate(value, lang) + ' ' + jtime(value, lang)

@register.filter
def jinterval(interval):
    data = localdata(interval)
    trans_str = _("On %(date)s from %(stime)s to %(etime)s for event %(event)s") \
        %{ "date": jdate(data.get('date')), "stime": jtime(data.get('start')),
            "etime": jtime(data.get('finish')), "event": interval.event.title
        }
    return trans_str

