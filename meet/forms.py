from models import *
from notification import invite_new_guests
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import fields
from meet.exceptions import UserIsNotInvitedException
from django.forms.extras.widgets import SelectDateWidget
from meet.templatetags import i18n
from django.utils import timezone
import pytz

class ValidationException (Exception):
	pass

class TitleDescriptionForm(forms.ModelForm):
	title = fields.CharField(widget=forms.TextInput(attrs={'placeholder': _("Enter the title of you event.")}), max_length = 30, label=_("Title"))
	description = fields.CharField(widget=forms.Textarea(attrs={'placeholder': _("Enter the Description of you event.")}), label=_("Description"))
	class Meta:
		model = Event
		fields = ('title', 'description', )


class GuestListForm(forms.ModelForm):
	guests = fields.CharField(widget=forms.Textarea(attrs={'placeholder': _("Enter the emails of guests you want to invite.")}), label=_("Guests"), required=True, error_messages={'required': _('You should enter at least one guest.')})
	deadline = fields.DateTimeField(widget=forms.HiddenInput(), required=False)
	year = fields.ChoiceField(label=_('Year'))
	month = fields.ChoiceField(label=_('Month'))
	day = fields.ChoiceField(label=_('Day'))
	hour = fields.ChoiceField(label=_('Hour'))
	
	class Meta:
		model = Event
		fields = ('guests', 'deadline', 'year', 'month', 'day', 'hour')

	@classmethod
	def get_users_with_these_emails(cls, emails_string):
		l = emails_string.replace(' ', '').replace('\n', '').replace('\r', '').split(',')
		invite_new_guests(l)
		users = User.objects.filter(email__in=l)
		return users

	def __init__(self, *args, **kwargs):
		super(GuestListForm, self).__init__(*args, **kwargs)
		g_today = timezone.now().date()
		j_this_year = i18n.topersiandate(g_today)[0]
		year_choices = [(i, i18n.iranian_digits(i)) for i in xrange(j_this_year,j_this_year+10)]
		self.fields['year'].choices = year_choices
		month_choices = [(i+1, i18n.PERSIAN_MONTHS[i]) for i in xrange(0,12)]
		self.fields['month'].choices = month_choices
		day_choices = [(i,i18n.iranian_digits(i)) for i in xrange(1,32)]
		self.fields['day'].choices = day_choices
		hour_choices = [(i,i18n.iranian_digits(i)) for i in xrange(0,24)]
		self.fields['hour'].choices = hour_choices

	def clean(self):
		cleaned_data = super(GuestListForm, self).clean()
		if not self._errors:
			try:
				utc = pytz.UTC
				cleaned_data['guest_list'] = GuestListForm.get_users_with_these_emails(cleaned_data.get('guests'))
				date_year = cleaned_data.get('year')
				date_month = cleaned_data.get('month')
				date_day = cleaned_data.get('day')
				hour = cleaned_data.get('hour')
				date = i18n.persiandate(int(date_year), int(date_month), int(date_day))
				tz = timezone.get_current_timezone()
				date_time = tz.localize(timezone.datetime(date.year, date.month, date.day, int(hour)))
				utc_time = utc.normalize(date_time.astimezone(utc))
				cleaned_data['deadline'] = utc_time
			except forms.ValidationError:
				self._errors['guests'] = self.error_class([_("You should enter at least one guest and guests' emails should be valid.")])

		return cleaned_data


class IntervalForm (forms.ModelForm):
	class Meta:
		model = Interval
		fields = ('event', 'date_year', 'date_month', 'date_day','start', 'finish', 'date')
	event = forms.ModelChoiceField(queryset=Event.objects.all())
	date_year = fields.ChoiceField(label=_('Year'))
	date_month = fields.ChoiceField(label=_('Month'))
	date_day = fields.ChoiceField(label=_('Day'))
	start = fields.TimeField(widget=forms.TextInput(attrs={'placeholder':_('Time format HH:MM')}))
	finish = fields.TimeField(widget=forms.TextInput(attrs={'placeholder':_('Time format HH:MM')}))
	date = fields.CharField(widget=forms.HiddenInput(), required=False)

	def __init__(self, *args, **kwargs):
		super(IntervalForm, self).__init__(*args, **kwargs)
		g_today = timezone.now().date()
		j_this_year = i18n.topersiandate(g_today)[0]
		year_choices = [(i, i18n.iranian_digits(i)) for i in xrange(j_this_year,j_this_year+10)]
		self.fields['date_year'].choices = year_choices
		month_choices = [(i+1, i18n.PERSIAN_MONTHS[i]) for i in xrange(0,12)]
		self.fields['date_month'].choices = month_choices
		day_choices = [(i,i18n.iranian_digits(i)) for i in xrange(1,32)]
		self.fields['date_day'].choices = day_choices

	def clean(self):
		cleaned_data = super(IntervalForm,self).clean()
		if not self._errors:
			date_year = cleaned_data.get('date_year')
			date_month = cleaned_data.get('date_month')
			date_day = cleaned_data.get('date_day')
			date = i18n.persiandate(int(date_year), int(date_month), int(date_day))
			tz = timezone.get_current_timezone()
			utc = pytz.UTC
			start_time = cleaned_data.get('start')
			start_date_time = tz.localize(timezone.datetime(date.year, date.month, date.day, start_time.hour, start_time.minute))
			finish_time = cleaned_data.get('finish')
			finish_date_time = tz.localize(timezone.datetime(date.year, date.month, date.day, finish_time.hour, finish_time.minute))
			utc_start = utc.normalize(start_date_time.astimezone(utc))
			utc_finish = utc.normalize(finish_date_time.astimezone(utc))
			cleaned_data['date'] = date
			cleaned_data['start'] = utc_start.time()
			cleaned_data['finish'] = utc_finish.time()
		return cleaned_data

class VoteForm (forms.ModelForm):
	interval = forms.ModelChoiceField(queryset=Interval.objects.all(), widget=forms.HiddenInput())
	voter = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
	state = forms.ChoiceField(choices=Vote.VOTE,  widget=forms.RadioSelect,
	label=_("If this event is being held in this time"))

	class Meta:
		model = Vote
		fields = ('state', 'interval', 'voter')

	def clean(self):
		cleaned_data = super(VoteForm,self).clean()
		if not self._errors:
			user = cleaned_data.get('voter')
			interval = cleaned_data.get('interval')
			state = cleaned_data.get('state')
			if not user.is_invited_to(interval.event):
				raise UserIsNotInvitedException
			if state and not state in [option[0] for option in Vote.VOTE]:
				self._errors['state'].append(self.error_class([_('Unacceptable state.')]))

		return cleaned_data


class EventTypeForm(forms.Form):
	Choices = [('1',_('Event')), ('2', _('Meeting')),]
	event_type = forms.ChoiceField(choices=Choices, widget=forms.RadioSelect, label=_("Event or Meeting"), error_messages={'required': _('You should choose one type.')})

	def clean(self):
		cleaned_data = super(EventTypeForm, self).clean()
		if not self._errors:
			ev_type = cleaned_data.get('event_type')
			available_choices = [ch[0] for ch in self.Choices]
			if not ev_type in available_choices:
				error_msg = _('The event type you requested is not provided!')
				self._errors['event_type'].append(error_msg)

		return cleaned_data


class MeetingConditionsForm(forms.Form):
	conditions = forms.ChoiceField(choices=[], widget=forms.RadioSelect, label=_("How should your meeting be closed?"), error_messages={'required': _('You should choose one type.')})
	
	def __init__(self, *args, **kwargs):
		super(MeetingConditionsForm, self).__init__(*args, **kwargs)
		choices = [(key, ClosingCondition.key_to_description_map[key]) for key in ClosingCondition.condition_keys]
		self.fields['conditions'].choices = choices

	def clean(self):
		cleaned_data = super(MeetingConditionsForm, self).clean()
		if not self._errors:
			cond = cleaned_data.get('conditions')
			available_choices = [ch[0] for ch in self.fields['conditions'].choices]
			if not cond in available_choices:
				error_msg = _('The condition type you requested for your event is not provided!')
				self._errors['conditions'].append(self.error_class([error_msg]))
		return cleaned_data


class AdvancedClosingConditionForm(forms.ModelForm):
	class Meta:
		model = AdvancedClosingCondition
		fields = ('must_come_list',)

	def __init__(self, guests=None, *args, **kwargs):
		guests = guests
		super(AdvancedClosingConditionForm, self).__init__(*args, **kwargs)
		self.fields['must_come_list'].choices = [(guest.id, guest.email) for guest in guests]

	def clean(self):
		#TODO: check that must come list is in guests of meeting
		cleaned_data = super(AdvancedClosingConditionForm, self).clean()
		if not self._errors:
			imp_guests = cleaned_data.get('must_come_list')
			all_users = User.objects.all()
			for guest in imp_guests:
				if not guest in all_users:
					error_msg = _('guest ' + guest.email + ' is not registered in the system')
					self._errors['must_come_list'].append(self.error_class([error_msg]))

		return cleaned_data
