from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from meet.models import Event, Interval
from meet.notification import *
from forms import *
from django.contrib.auth.models import User
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.contrib.formtools.wizard.views import CookieWizardView
from django.forms.models import inlineformset_factory, modelformset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import ugettext_lazy as _
from MeetMe import settings
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponseForbidden
from meet.exceptions import UserIsNotInvitedException
import datetime, pytz
from datetime import timedelta as td


def can_close(user):
	if user.has_perm('admin'):
		return True
	else:
		raise PermissionDenied

def home (request):
	if not request.session.has_key('_auth_user_id'):
		return render_to_response('index.html', {
		})
	user_id = request.session['_auth_user_id']
	user = User.objects.get(id=user_id)
	utctime = timezone.now()
	localtime = timezone.localtime(utctime)
	day_of_week = (localtime.weekday()+2)%7
	days_before = 14 + day_of_week
	days_after = 21 - day_of_week
	start_date = (localtime+td(days=-days_before)).date()
	end_date = (localtime+td(days=days_after)).date()
	days = []
	cal_list = []	
	for i in xrange(0,35):
		days.append(start_date+td(days=i))
		if len(days)==7:
			cal_list.append([ (day, user.meetings_on(day)) for day in days])
			days=[]
	day_of_week = int(utctime.strftime("%w"))
	notifications = user.get_related_unread_notifications()
	farsi_tzs = [_(tz) for tz in pytz.common_timezones]
	return render(request, 'home.html', {
		'email': user.email,
		'username' : user.username,
		'timezone' : timezone.get_current_timezone_name(),
		'is_admin': user.has_perm('admin'),
		'today' : localtime.date(),
		'cal_list' : cal_list,
		'start_date': start_date,
		'end_date' : end_date,
		'notifications': notifications,
		'danger': Notification.DANGER,
		'inform': Notification.INFORM,
		'view_name' : 'Home',
		'timezones': pytz.common_timezones,
	})

def set_timezone(request):
	if request.method == 'POST':
		request.session['django_timezone'] = request.POST['timezone']
		return redirect('/')
	else:
		return render(request, 'timezone_sel.html', {'timezones': pytz.common_timezones})

@login_required
def vote_event (request, event_id):
	event = Event.objects.get(id=event_id)
	options = event.options_list.all()
	user = request.user
	if not user.is_invited_to(event):
		raise PermissionDenied
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
	return render_to_response('event_vote.html', {
		'event_id' : event_id,
		'votes'  : votes,
		'management_form': pfilled_form.management_form,
	}, context_instance = RequestContext(request))

@login_required
def view_event (request, event_id):
	event = Event.objects.get(id=event_id)
	# options = event.options_list.all()
	# user = request.user
	# if not user.is_invited_to(event):
		# raise PermissionDenied
	# FormSet = formset_factory(VoteForm)
	# initial_data = {'form-TOTAL_FORMS': u''+str(len(options)),
					# 'form-INITIAL_FORMS': u''+str(len(options)),
					# 'form-MAX_NUM_FORMS': u'',
	# }
	# for i in xrange(len(options)):
		# initial_data['form-'+str(i)+'-voter']= user.id
		# initial_data['form-'+str(i)+'-interval']= options[i].id
	# pfilled_form = FormSet(initial_data)
	# votes = [ {'option': option, 'form': form} for option, form in zip(options, pfilled_form)]
	return render_to_response('event_view.html', {
		'event' : event,
		# 'votes'  : votes,
		# 'management_form': pfilled_form.management_form,
	}, context_instance = RequestContext(request))

@login_required
def related_events(request, msg=None):
	user=request.user
	events_to_show = user.related_events();
	events = [{'event':event, 'is_vote_cast':event.has_user_voted(user), 
	'is_meeting': hasattr(event, 'meeting'), 'is_closed': (event.status==Event.CLOSED),
	'is_owner': (event.creator==user), 'is_google_calendarizable': event.is_google_calendarizable()} for event in events_to_show]
	return render_to_response('related_events.html',{
		'events' : events,
		'message': msg, 
	})

@login_required
def mark_notif_read(request, notif_id):
	notif = Notification.objects.get(id=notif_id)
	if notif.recipient == request.user.email:
		notif.mark_as_seen()
		return redirect('/')
	else:
		return HttpResponseForbidden()

@login_required
def vote (request):
	event_id = request.POST['event_id']	
	usr = request.user
	filled_forms = formset_factory(VoteForm)
	validation_data = filled_forms(request.POST)
	message = 'Your voted for event with id "'+ event_id + '" successfully.' 
	if validation_data.is_valid():
		try:
			for form in validation_data.forms:
				interval = form.cleaned_data['interval']
				try:
					current_vote = interval.get_vote(usr)
					current_vote.update_state(form.cleaned_data['state'])
				except ObjectDoesNotExist, e:
					form.save()
		except UserIsNotInvitedException, e:
			raise PermissionDenied
	else:
		message = 'Your could not event with id "' + event_id + '".'
	return related_events(request, message)	




@login_required
@user_passes_test(can_close)
def admin_review (request, msg=None):
	meetings = Meeting.get_waiting_for_admin_meetings()
	return render(request, 'close_meeting.html' ,
		{'meetings':meetings,
		'msg': msg, })


@login_required
@user_passes_test(can_close)
def confirm_meeting(request, meeting_id):
	meeting = Meeting.objects.get(id=meeting_id)
	meeting.confirm()
	guest_emails = meeting.get_guest_emails()
	for email in guest_emails:
		notif = InformConfirmToGuestsNotification()
		notif.recipient = email
		notif.meeting = meeting
		notif.save()
	notif = InformConfirmToCreatorNotification()
	notif.recipient = meeting.get_creator_email()
	notif.meeting = meeting
	notif.save()
	return admin_review(request, _("The Meeting named "+ meeting.title +" was confirmed successfully."))


@login_required
@user_passes_test(can_close)
def cancel_meeting(request, meeting_id):
	meeting = Meeting.objects.get(id=meeting_id)
	meeting.cancel()
	guest_emails = meeting.get_guest_emails()
	for email in guest_emails:
		notif = InformCancelToGuestsNotification()
		notif.recipient = email
		notif.meeting = meeting
		notif.save()
	notif = InformCancelToCreatorNotification()
	notif.recipient = meeting.get_creator_email()
	notif.meeting = meeting
	notif.save()
	return admin_review(request, _("The Meeting named "+ meeting.title +" was canceled successfully."))

@login_required
def revote(request, event_id):
	event = get_object_or_404(Event, Q(id=event_id, creator=request.user))
	votes = Vote.objects.filter(interval__event=event)
	for vote in votes:
		vote.delete() 
	return related_events(request, _('Your revote for event "' + event.title +'" is done successfully.'))


class CreateWizard(CookieWizardView):

	def remove_old_data(self, event):
		intervals = event.options_list.all()
		# votes = Vote.objects.filter(interval__event=event)
		# for vote in votes:
		# 	vote.delete()
		for interval in intervals:
			interval.delete()

		if is_meeting(self):
			closing_condition = ClosingCondition.objects.get_subclass(meeting=event)
			closing_condition.delete()

	def set_meeting_data(self, event):
		meeting_cond_key = self.get_cleaned_data_for_step('4')['conditions']
		meeting = Meeting(event_ptr_id=event.pk)
		meeting.__dict__.update(event.__dict__)
		closing_condition = ClosingCondition.key_to_type_map[meeting_cond_key]()
		meeting.save()
		closing_condition.meeting = meeting
		closing_condition.save()
		if is_advanced(self):
			closing_condition.must_come_list = self.get_cleaned_data_for_step('5')['must_come_list']
			closing_condition.save()

	def save_event(self, event_form):
		event = event_form.save(commit=False)
		creator = self.request.user
		event.creator = creator
		event_deadline =  self.get_cleaned_data_for_step('1')['deadline']
		event.deadline =  event_deadline
		guest_list =  self.get_cleaned_data_for_step('1')['guest_list']
		event.save()
		event.guest_list = guest_list
		event.save()
		return event

	def set_intervals(self, event, interval_forms):
		intervals = interval_forms.save(commit=False)
		for interval in intervals:
			interval.event_id = event.id
			interval.save()

	def done(self, form_list, **kwargs):
		event_form = form_list[0]
		event = self.save_event(event_form)
		if not is_create_wizard(self):
			self.remove_old_data(event)
		interval_forms = form_list[2]
		self.set_intervals(event, interval_forms)
		if is_meeting(self):
			self.set_meeting_data(event)
		if is_create_wizard(self):
			msg = _("Your event named "+ event.title +" was added successfully.")
		else:
			msg = _("Your event named "+ event.title +" was edited and saved successfully.\
			 You should perform a revote so that users can vote again.")
		
		return related_events(self.request, msg)

	def get_template_names(self):
		return 'create_event.html'


def is_create_wizard(wizard):
	if wizard.instance_dict:
		return False
	else:
		return True


def is_meeting(wizard):
	if not is_create_wizard(wizard):
		return True if hasattr(wizard.instance_dict['0'], 'meeting') else False
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


@login_required
def create_wizard (request):
	create_wizard_as_view =CreateWizard.as_view([TitleDescriptionForm, GuestListForm, 
		inlineformset_factory(Event, Interval, max_num=1, extra=3), EventTypeForm, MeetingConditionsForm, AdvancedClosingConditionForm],
		condition_dict={'4': is_meeting, '5': is_advanced}
		)
	return create_wizard_as_view(request)


@login_required
def edit_wizard (request, event_id):
	event = get_object_or_404(Event, Q(id=event_id))#, Q(creator=request.user))
	instance_dictionary = {'0': event, '1': event,}
	initial_dict = {}
	if hasattr(event, 'meeting'):
		closing_condition = ClosingCondition.objects.get_subclass(meeting=event)
		initial_dict = {
			'4': {'conditions': closing_condition.key, },
		}

	edit_wizard_as_view =CreateWizard.as_view([TitleDescriptionForm, GuestListForm,
		inlineformset_factory(Event, Interval, max_num=1, extra=3), EventTypeForm, MeetingConditionsForm, AdvancedClosingConditionForm],
		instance_dict=instance_dictionary,
		initial_dict=initial_dict,
		condition_dict={'3': is_create_wizard, '4': is_meeting, '5': is_advanced}
		)
	return edit_wizard_as_view(request)

