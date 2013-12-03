from models import *
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import fields


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
				self.add_error('guests', 'guest ' + guest.email + ' is not registered in the system').
		return cleaned_data



class VoteForm (forms.ModelForm):
	interval = forms.ModelChoiceField(queryset=Interval.objects.all(), widget=forms.HiddenInput())
	voter = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
	class Meta:
		model = Vote
		fields = ('state', 'interval', 'voter')


class EventForm (forms.ModelForm):
	title = fields.CharField(widget=forms.TextInput(attrs={'placeholder': _("Enter the title of you event.")}), max_length = 30, label=_("Title"))
	description = fields.CharField(widget=forms.Textarea(attrs={'placeholder': _("Enter the Description of you event.")}), label=_("Description"))

	class Meta:
		model = Event
		fields = ('title', 'description', 'guest_list', )


class EventTypeForm(forms.Form):
	Choices = [('1','Event'), ('2', 'Meeting'),]
	event_type = forms.ChoiceField(choices=Choices, label="Event or Meeting", error_messages={'required': _('You should choose one type.')})
	# event_type = fields.MultipleChoiceField(choices=Choices)



class MeetingConditionsForm(forms.Form):
	conditions = forms.ChoiceField(choices=[], label="How should your meeting be closed?", error_messages={'required': _('You should choose one type.')})
	
	def __init__(self, *args, **kwargs):
		super(MeetingConditionsForm, self).__init__(*args, **kwargs)
		choices = [(key, ClosingCondition.key_to_description_map[key]) for key in ClosingCondition.condition_keys]
		self.fields['conditions'].choices = choices
