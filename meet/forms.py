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
		fields = ('guest_list', )


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
