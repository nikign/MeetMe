from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from meet.models import Event, Interval
from meet.notification import inform_confirm, inform_cancel, inform_reservation, Notification
from meet.forms import *
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
from meet.utils.utils import localdata

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
	end_date = (localtime+td(days=days_after-1)).date()
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
		'timezones': pytz.common_timezones,
		'is_admin': user.has_perm('admin'),
		'today' : localtime.date(),
		'cal_list' : cal_list,
		'start_date': start_date,
		'end_date' : end_date,
		'notifications': notifications,
		'danger': Notification.DANGER,
		'inform': Notification.INFORM,
		'view_name' : _('Home'),
		'is_admin' : user.has_perm('admin'),
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
	
	joptions = [localdata(option) for option in options]
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
	votes = [ {'option': option, 'form': form} for option, form in zip(joptions, pfilled_form)]
	return render_to_response('event_vote.html', {
		'event_id' : event_id,
		'votes'  : votes,
		'management_form': pfilled_form.management_form,
		'username' : request.user.username,
		'timezone' : timezone.get_current_timezone_name(),
		'timezones': pytz.common_timezones,
		'view_name': _('Vote'),
		'is_admin' : user.has_perm('admin'),
	}, context_instance = RequestContext(request))

@login_required
def view_event (request, event_id):
	event = Event.objects.get(id=event_id)
	deadline = event.deadline
	jdeadline = timezone.localtime(deadline)
	return render_to_response('event_view.html', {
		'event' : event,
		'status' : event.get_status_message(),
		'deadline' : jdeadline,
		'username' : request.user.username,
		'timezone' : timezone.get_current_timezone_name(),
		'timezones': pytz.common_timezones,
		'view_name' : event.title,
		'is_admin' : request.user.has_perm('admin'),
	}, context_instance = RequestContext(request))

@login_required
def related_events(request, msg=None):
	user=request.user
	events_to_show = user.related_events();
	events = [{'event':event, 'is_vote_cast':event.has_user_voted(user), 
	'is_meeting': hasattr(event, 'meeting'), 'is_closed': (event.status==Event.CLOSED),
	'is_cancelled': hasattr(event, 'meeting') and event.meeting.confirmed == Meeting.CANCELLED,
	'is_owner': (event.creator==user), 'is_google_calendarizable': event.is_google_calendarizable()} for event in events_to_show]
	username = request.user.username
	return render_to_response('related_events.html',{
		'events' : events,
		'message': msg, 
		'user': user,
		'username' : username,
		'timezone' : timezone.get_current_timezone_name(),
		'timezones': pytz.common_timezones,
		'view_name' : _("%s's Events") % username,
		'is_admin' : user.has_perm('admin'),
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
	event_name = Event.objects.get(id=event_id).title
	usr = request.user
	filled_forms = formset_factory(VoteForm)
	validation_data = filled_forms(request.POST)
	message = _('You voted for event "%s" successfully.') %event_name
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
		message = _('You could not vote on event "%s".') %event_name
	return related_events(request, message)	


@login_required
@user_passes_test(can_close)
def admin_review (request, msg=None):
	meetings = Meeting.get_waiting_for_admin_meetings()
	user=request.user
	return render(request, 'close_meeting.html' ,
		{'meetings':meetings,
		'msg': msg,
		'username' : request.user.username,
		'timezone' : timezone.get_current_timezone_name(),
		'timezones': pytz.common_timezones,
		'view_name' : _('Admin Review'),
		'is_admin' : user.has_perm('admin'),})


@login_required
@user_passes_test(can_close)
def confirm_meeting(request, meeting_id):
	meeting = Meeting.objects.get(id=meeting_id)
	meeting.confirm()
	inform_confirm(meeting)
	return admin_review(request, _("The Meeting named %s was confirmed successfully.") %meeting.title)


@login_required
@user_passes_test(can_close)
def cancel_meeting(request, meeting_id):
	meeting = Meeting.objects.get(id=meeting_id)
	meeting.cancel()
	inform_cancel(meeting)
	return admin_review(request, _("The Meeting named %s was canceled successfully.") %meeting.title)

@login_required
def revote(request, event_id):
	event = get_object_or_404(Event, Q(id=event_id, creator=request.user))
	votes = Vote.objects.filter(interval__event=event)
	for vote in votes:
		vote.delete()
	event.open_again()
	inform_revote(event)
	return related_events(request, _('Your revote for event "%s" is done successfully.') %event.title)


def handler404(request):
	message = _("404! The page you requested was not found!")
	return render(request, 'errors.html', {'message': message,
											'username' : request.user.username,
											'timezone' : timezone.get_current_timezone_name(),
											'timezones': pytz.common_timezones,
											'view_name' : _('404'),
											'is_admin' : request.user.has_perm('admin'),})


def handler403(request):
	message = _("403! You Don't have permission to access this page!")
	return render(request, 'errors.html', {'message': message,
											'username' : request.user.username,
											'timezone' : timezone.get_current_timezone_name(),
											'timezones': pytz.common_timezones,
											'view_name' : _('403'),
											'is_admin' : request.user.has_perm('admin'),})


def handler500(request):
	message = _("500! Something went wrong with our server. We are sorry!")
	return render(request, 'errors.html', {'message': message,
											'username' : request.user.username,
											'timezone' : timezone.get_current_timezone_name(),
											'timezones': pytz.common_timezones,
											'view_name' : _('500'),
											'is_admin' : request.user.has_perm('admin'),})


class CreateWizard(CookieWizardView):

	def get_context_data(self, form, **kwargs):
		context = super(CreateWizard, self).get_context_data(form=form, **kwargs)
		context.update({'email': self.request.user.email,
		'username' : self.request.user.username,
		'timezone' : timezone.get_current_timezone_name(),
		'timezones': pytz.common_timezones,})
		if is_create_wizard(self):
			context.update({'view_name' : _('Create'),'is_admin':self.request.user.has_perm('admin')})
		else:
			context.update({'view_name' : _('Edit'),'is_admin':self.request.user.has_perm('admin')})

		return context


	def remove_old_data(self, event):
		intervals = event.options_list.all()
		for interval in intervals:
			interval.delete()

		if is_meeting(self):
			closing_condition = ClosingCondition.objects.get_subclass(meeting=event)
			closing_condition.delete()

	def get_form_kwargs(self, step=None):
		step = step or self.steps.current
		if step == '5':
			return {'guests': self.get_cleaned_data_for_step('1')['guest_list'], }
		else:
			return {}

	def check_existance_of_intervals_and_guests(self, interval_forms):
		intervals = interval_forms.save(commit=False)
		if len(intervals)==0 :
			self.render_revalidation_failure('2', inlineformset_factory(Event, Interval, max_num=1, extra=3, form=IntervalForm))


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
		if is_create_wizard(self):
			invite_guests(event)
		return event

	def set_intervals(self, event, interval_forms):
		intervals = interval_forms.save(commit=False)
		for interval in intervals:
			interval.event_id = event.id
			interval.save()

	def done(self, form_list, **kwargs):
		event_form = form_list[0]
		event = self.save_event(event_form)
		interval_forms = form_list[2]
		self.check_existance_of_intervals_and_guests(interval_forms)
		if not is_create_wizard(self):
			self.remove_old_data(event)
		self.set_intervals(event, interval_forms)
		if is_meeting(self):
			self.set_meeting_data(event)
		
		if is_create_wizard(self):
			msg = _("Your event named %s was added successfully.") %event.title
		else:
			msg = _("Your event named %s was edited and saved successfully. You should perform a revote so that users can vote again.") %event.title
		
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
		inlineformset_factory(Event, Interval, max_num=1, extra=3, form=IntervalForm), EventTypeForm, MeetingConditionsForm, AdvancedClosingConditionForm],
		condition_dict={'4': is_meeting, '5': is_advanced}
		)
	return create_wizard_as_view(request)


@login_required
def edit_wizard (request, event_id):
	event = get_object_or_404(Event, Q(id=event_id), Q(creator=request.user))
	instance_dictionary = {'0': event, '1': event,}
	guests = [guest.email for guest in event.guest_list.all()]
	guest_string = ",".join(guests)
	initial_dict = {}
	if hasattr(event, 'meeting'):
		closing_condition = ClosingCondition.objects.get_subclass(meeting=event.meeting)
		initial_dict = {
			'4': {'conditions': closing_condition.key, },
		}
		if hasattr(closing_condition, 'must_come_list'):
			initial_dict['5'] = {'must_come_list': closing_condition.must_come_list.all() }
			
	initial_dict['1'] = {'guests': guest_string, 'deadline': event.deadline, }
	edit_wizard_as_view =CreateWizard.as_view([TitleDescriptionForm, GuestListForm,
		inlineformset_factory(Event, Interval, max_num=1, extra=3, form=IntervalForm), EventTypeForm, MeetingConditionsForm, AdvancedClosingConditionForm],
		instance_dict=instance_dictionary,
		initial_dict=initial_dict,
		condition_dict={'3': is_create_wizard, '4': is_meeting, '5': is_advanced}
		)
	return edit_wizard_as_view(request)

