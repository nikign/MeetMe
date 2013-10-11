from models import *
from django import forms

class TitleDescriptionForm(forms.ModelForm):
	class Meta:
		model = Event
		fields = ('title', 'description', )

class GuestListForm(forms.ModelForm):
	class Meta:
		model = Event
		fields = ('guest_list', )