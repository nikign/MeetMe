from django.shortcuts import render_to_response, render
from models import Event
from forms import *
from django.contrib.auth.models import User
from django.template import RequestContext
from django.forms.formsets import formset_factory

def home (request):
	return render_to_response('home.html')

def view (request, event_id):
	event = Event.objects.get(id=event_id)
	options = event.options_list.all()
	user = User.objects.all()[0]
	# votes = [(option, VoteOptionForm(initial={'interval':option.id})) for option in options]
	FormSet = formset_factory(VoteForm)
	initial_data = {'form-TOTAL_FORMS': u''+str(len(options)),
					'form-INITIAL_FORMS': u''+str(len(options)),
					'form-MAX_NUM_FORMS': u'',
	}
	for i in xrange(len(options)):
		initial_data['form-'+str(i)+'-voter']= user.id
		initial_data['form-'+str(i)+'-interval']= options[i].id
	votes = [ {'option': option, 'form': form} for option, form in zip(options, FormSet(initial_data))]
	return render_to_response('event.html', {
		'event_id' : event_id,
		'votes'  : votes,
	}, context_instance = RequestContext(request))

def vote (request):
	event_id = request.POST['event_id']	
	return render_to_response('vote.html', {
		'post' : request.POST
	}, context_instance = RequestContext(request))	

def test(request):
	title_description_form = TitleDescriptionForm()
	guests_form = GuestListForm()
	return render(request, 'test.html', {'title_form': title_description_form, 'guests_form': guests_form, })
