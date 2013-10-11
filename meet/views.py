from django.shortcuts import render_to_response, render
from models import Event
from forms import TitleDescriptionForm, GuestListForm

def home (request):
	return render_to_response('home.html')

def view (request, event_id):
	event = Event.objects.get(id=event_id)
	options = event.options_list.all()
	return render_to_response('event.html', {
		'event_id' : event_id,
		'options'  : options,
	})


def test(request):
	title_description_form = TitleDescriptionForm()
	guests_form = GuestListForm()
	return render(request, 'test.html', {'title_form': title_description_form, 'guests_form': guests_form, })
