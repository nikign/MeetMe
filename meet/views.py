from django.shortcuts import render_to_response, render
from models import Event, Interval
from forms import *
from django.contrib.auth.models import User
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.contrib.formtools.wizard.views import SessionWizardView
from django.forms.models import inlineformset_factory, modelformset_factory

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

def create(request):
	# title_description_form = TitleDescriptionForm()
	# types_form = EventTypeForm()
	# IntervalFormSet = modelformset_factory(Interval, max_num=2, extra=3)
	IntervalFormSet = inlineformset_factory(Event, Interval, can_delete=True, max_num=2, extra=3)
	event_form = EventForm()
	return render(request, 'test.html', {'event_form': event_form, 'interval_form': IntervalFormSet(), })


def save_event(request):
	print "inja save evente!"
	form = EventForm(request.POST)
	if form.is_valid():
		form.save()
	# 'options_list-1-'+i
	IntervalFormSet = inlineformset_factory(Event, Interval, can_delete=True, max_num=2, extra=3)
	interval_form = IntervalFormSet(request.POST)

	intervals = interval_form.save(commit=False)
	for interval in intervals:
		interval.event_id
	return render_to_response('vote.html', {
		'post' : "success"
	}, context_instance = RequestContext(request))	


class CreateWizard(SessionWizardView):
	def done(self, form_list, **kwargs):
		return render_to_response('done.html', {
			'form_data': [form.cleaned_data for form in form_list],
		})

	def get_template_names(self):
		return 'test.html'

create_wizard = CreateWizard.as_view([TitleDescriptionForm, EmptyForm, EventTypeForm,])
