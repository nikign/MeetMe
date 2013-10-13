from models import *
from django import forms

class ValidationException (Exception):
	pass

class TitleDescriptionForm(forms.ModelForm):
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
		fields = ( 'state', 'interval', 'voter')