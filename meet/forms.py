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
		fields = ('state', 'interval', 'voter')


class EmptyForm(forms.Form):
	pass

class EventTypeForm(forms.Form):
    event_type = forms.ChoiceField(widget=forms.RadioSelect, choices=[])

    def __init__(self, *args, **kwargs):
        super(EventTypeForm, self).__init__(*args, **kwargs)
        self.fields['event_type'].choices = [('1','Event'), ('2', 'Meeting'), ]

class EventForm (forms.ModelForm):
	class Meta:
		model = Event
