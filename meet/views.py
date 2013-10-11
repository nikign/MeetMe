from django.shortcuts import render_to_response
from models import Event
from forms import TitleDescriptionForm

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
	my_form = TitleDescriptionForm()
	return render(request, 'advertisers/test.html', {'title_form': my_form, })
