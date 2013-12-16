from models import *
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import fields
from meet.exceptions import UserIsNotInvitedException

class ValidationException (Exception):
	pass

class TitleDescriptionForm(forms.ModelForm):
	title = fields.CharField(widget=forms.TextInput(attrs={'placeholder': _("Enter the title of you event.")}), max_length = 30, label=_("Title"))
	description = fields.CharField(widget=forms.Textarea(attrs={'placeholder': _("Enter the Description of you event.")}), label=_("Description"))
	class Meta:
		model = Event
		fields = ('title', 'description', )


class GuestListForm(forms.ModelForm):
	
	class Meta:
		model = Event
		fields = ('guest_list', 'deadline' )

	def clean(self):
		cleaned_data = super(GuestListForm, self).clean()
		guests = cleaned_data.get('guest_list')
		all_users = User.objects.all()
		for guest in guests:
			if not guest in all_users:
				error_msg =  'guest ' + guest.email + ' is not registered in the system'
				self._errors['guests'].append(self.error_class([error_msg]))

		return cleaned_data


class VoteForm (forms.ModelForm):
	interval = forms.ModelChoiceField(queryset=Interval.objects.all(), widget=forms.HiddenInput())
	voter = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
	state = forms.ChoiceField(choices=Vote.VOTE,  widget=forms.RadioSelect, label="Will you attend the event at this time?")

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
			self._errors['state'].append(self.error_class(['Unacceptable state.']))

		return cleaned_data


class EventTypeForm(forms.Form):
	Choices = [('1','Event'), ('2', 'Meeting'),]
	event_type = forms.ChoiceField(choices=Choices, widget=forms.RadioSelect, label="Event or Meeting", error_messages={'required': _('You should choose one type.')})

	def clean(self):
		cleaned_data = super(EventTypeForm, self).clean()
		ev_type = cleaned_data.get('event_type')
		available_choices = [ch[0] for ch in self.Choices]
		if not ev_type in available_choices:
			error_msg = 'The event type you requested is not provided!'
			self._errors['event_type'].append(error_msg)

		return cleaned_data


class MeetingConditionsForm(forms.Form):
	conditions = forms.ChoiceField(choices=[], widget=forms.RadioSelect, label="How should your meeting be closed?", error_messages={'required': _('You should choose one type.')})
	
	def __init__(self, *args, **kwargs):
		super(MeetingConditionsForm, self).__init__(*args, **kwargs)
		choices = [(key, ClosingCondition.key_to_description_map[key]) for key in ClosingCondition.condition_keys]
		self.fields['conditions'].choices = choices

	def clean(self):
		cleaned_data = super(MeetingConditionsForm, self).clean()
		cond = cleaned_data.get('conditions')
		available_choices = [ch[0] for ch in self.fields['conditions'].choices]
		if not cond in available_choices:
			error_msg = 'The condition type you requested for your event is not provided!'
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
				error_msg = 'guest ' + guest.email + ' is not registered in the system'
				self._errors['must_come_list'].append(self.error_class([error_msg]))

		return cleaned_data
