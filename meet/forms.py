from models import *
from notification import invite_new_guests
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import fields
from meet.exceptions import UserIsNotInvitedException
from django.forms.extras.widgets import SelectDateWidget
from meet.templatetags import i18n
from django.utils import timezone


class ValidationException (Exception):
	pass

class TitleDescriptionForm(forms.ModelForm):
	title = fields.CharField(widget=forms.TextInput(attrs={'placeholder': _("Enter the title of you event.")}), max_length = 30, label=_("Title"))
	description = fields.CharField(widget=forms.Textarea(attrs={'placeholder': _("Enter the Description of you event.")}), label=_("Description"))
	class Meta:
		model = Event
		fields = ('title', 'description', )


class GuestListForm(forms.ModelForm):
	guests = fields.CharField(widget=forms.Textarea(attrs={'placeholder': _("Enter the emails of guests you want to invite.")}), label=_("Guests"))
	deadline = fields.DateTimeField()
	class Meta:
		model = Event
		fields = ('guests', 'deadline', )

	@classmethod
	def get_users_with_these_emails(cls, emails_string):
		l = emails_string.replace(' ', '').replace('\n', '').replace('\r', '').split(',')
		invite_new_guests(l)
		users = User.objects.filter(email__in=l)
		return users

	def clean(self):
		cleaned_data = super(GuestListForm, self).clean()
		cleaned_data['guest_list'] = GuestListForm.get_users_with_these_emails(cleaned_data.get('guests'))
		# guests = cleaned_data.get('guest_list')
		all_users = User.objects.all()
		# for guest in guests:
		# 	if not guest in all_users:
		# 		error_msg =  _('guest ' + guest.email + ' is not registered in the system')
		# 		self._errors['guests'].append(self.error_class([error_msg]))

		return cleaned_data


class IntervalForm (forms.ModelForm):
	class Meta:
		model = Interval
		fields = ('event', 'date_year', 'date_month', 'date_day','start', 'finish')
	event = forms.ModelChoiceField(queryset=Event.objects.all())
	date_year = fields.ChoiceField(label=_('Year'))
	date_month = fields.ChoiceField(label=_('Month'))
	date_day = fields.ChoiceField(label=_('Day'))
	start = fields.CharField(widget=forms.TextInput(attrs={'placeholder':_('Time format HH:MM')}))
	finish = fields.CharField(widget=forms.TextInput(attrs={'placeholder':_('Time format HH:MM')}))
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

	def clean(self):
		#TODO: check that must come list is in guests of meeting
		cleaned_data = super(AdvancedClosingConditionForm, self).clean()
		imp_guests = cleaned_data.get('must_come_list')
		all_users = User.objects.all()
		for guest in imp_guests:
			if not guest in all_users:
				error_msg = _('guest ' + guest.email + ' is not registered in the system')
				self._errors['must_come_list'].append(self.error_class([error_msg]))

		return cleaned_data
