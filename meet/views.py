from django.shortcuts import render_to_response, render, redirect
from models import Event, Interval
from forms import *
from django.contrib.auth.models import User
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.contrib.formtools.wizard.views import CookieWizardView
from django.forms.models import inlineformset_factory, modelformset_factory
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from MeetMe import settings
from django.utils import timezone
import pytz
from django.core.exceptions import PermissionDenied

from meet.exceptions import UserIsNotInvitedException

def home (request):
	if not request.session.has_key('_auth_user_id'):
		return render_to_response('index.html', {
		})
	user_id = request.session['_auth_user_id']
	user = User.objects.get(id=user_id)
	utctime = timezone.now()
	return render_to_response('home.html', {
		'email': user.email,
		'username' : user.username,
		'timezone' : timezone.get_current_timezone_name(),
		'time' : utctime,
	})

def set_timezone(request):
	if request.method == 'POST':
		request.session['django_timezone'] = request.POST['timezone']
		return redirect('/')
	else:
		return render(request, 'timezone_sel.html', {'timezones': pytz.common_timezones})

@login_required
def view (request, event_id):
	event = Event.objects.get(id=event_id)
	options = event.options_list.all()
	user = request.user
	if not user.is_invited_to(event):
		raise PermissionDenied
	print user
	# votes = [(option, VoteOptionForm(initial={'interval':option.id})) for option in options]
	FormSet = formset_factory(VoteForm)
	initial_data = {'form-TOTAL_FORMS': u''+str(len(options)),
					'form-INITIAL_FORMS': u''+str(len(options)),
					'form-MAX_NUM_FORMS': u'',
	}
	for i in xrange(len(options)):
		initial_data['form-'+str(i)+'-voter']= user.id
		initial_data['form-'+str(i)+'-interval']= options[i].id
	pfilled_form = FormSet(initial_data)
	votes = [ {'option': option, 'form': form} for option, form in zip(options, pfilled_form)]
	return render_to_response('event.html', {
		'event_id' : event_id,
		'votes'  : votes,
		'management_form': pfilled_form.management_form,
	}, context_instance = RequestContext(request))

@login_required
def related_events(request):
	user=request.user
	events_to_show = user.related_events(0,10);
	events = [ {'event':event, 'is_vote_cast':event.has_user_voted(user)} for event in events_to_show]
	return render_to_response('related_events.html',{
		'events' : events,

	})

@login_required
def vote (request):
	event_id = request.POST['event_id']	
	filled_forms = formset_factory(VoteForm)
	validation_data = filled_forms(request.POST)
	message = 'SUCCESS'
	if validation_data.is_valid():
		try:
			for form in validation_data.forms:
				form.save()
		except UserIsNotInvitedException, e:
			raise PermissionDenied
	else:
		message = 'FAILURE'
	return render_to_response('vote.html', { 
		'post' : request.POST,
		'message' : message,
	}, context_instance = RequestContext(request))	

@login_required
def create(request):
	IntervalFormSet = inlineformset_factory(Event, Interval, max_num=1, extra=3)
	event_form = EventForm()
	return render(request, 'test.html', {'event_form': event_form, 'interval_form': IntervalFormSet(), })


def send_test_mail(request):
	from django.core.mail import EmailMultiAlternatives

	# email = EmailMultiAlternatives(subject='Test Mail', body="ma khe'li khafanim", 
	# 	from_email='info@meetme.ir', to=['story_ngn@yahoo.com'], cc=[], bcc=None,)
	email = EmailMultiAlternatives(subject='Test Mail', body="ma khafantarinim asan! :D :D :D", 
		from_email='info@meetme.ir', to=['niki.hp2007@gmail.com'], cc=['ashkan.dant3@gmail.com'], bcc=None,)
	# email.attach_alternative(body_html, "text/html")
	email.send()
	print "hasan o jafar o abbas o ali"

	return render_to_response('event_saved.html', {
		'message' : "Mail zadam.",
		'status' : 'khafan'
	})	



class CreateWizard(CookieWizardView):

	def done(self, form_list, **kwargs):
		form1 = form_list[0]
		event = form1.save(commit=False)
		event.creator = User.objects.all()[0]
		event_deadline =  self.get_cleaned_data_for_step('1')['deadline']
		event.deadline =  event_deadline
		# event1.creator = self.request.user
		guest_list =  self.get_cleaned_data_for_step('1')['guest_list']
		event.save()
		event.guest_list = guest_list
		event.save()
		interval_forms = form_list[2]
		intervals = interval_forms.save(commit=False)
		for interval in intervals:
			interval.event_id = event.id
			interval.save()
		if is_meeting(self):
			meeting_cond_key = self.get_cleaned_data_for_step('4')['conditions']
			meeting = Meeting(event_ptr_id=event.pk)
			meeting.__dict__.update(event.__dict__)
			# meeting.conditions = meeting_cond
			closing_condition = ClosingCondition.key_to_type_map[meeting_cond_key]()
			meeting.save()
			closing_condition.meeting = meeting
			closing_condition.save()
			print 'cond::::::::', meeting.closing_condition
			return render_to_response('event_saved.html', {
				'message': "You event named "+ event.title +" was added successfully.",
			})

		
		return render_to_response('event_saved.html', {
			'message': "You event named "+ event.title +" was added successfully.",
		})

	def get_template_names(self):
		return 'create_event.html'

def is_meeting(wizard):
	event_type_data = wizard.get_cleaned_data_for_step('3')['event_type'] if wizard.get_cleaned_data_for_step('3') else None
	if event_type_data == '2':
		return True
	else:
		return False

def is_advanced(wizard):
	conditions = wizard.get_cleaned_data_for_step('4')['conditions'] if wizard.get_cleaned_data_for_step('4') else None
	if conditions=='ad':
		return True
	return False

create_wizard = CreateWizard.as_view([TitleDescriptionForm, GuestListForm, 
	inlineformset_factory(Event, Interval, max_num=1, extra=3), EventTypeForm, MeetingConditionsForm, AdvancedClosingConditionForm],
	condition_dict={'4': is_meeting, '5': is_advanced}
	)

