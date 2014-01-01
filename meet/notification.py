from django.db import models
from django.contrib.contenttypes.models import ContentType
from model_utils.managers import InheritanceManager
from django.utils.translation import ugettext_lazy as _
from meet.models import *
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email


class Notification(models.Model):
	DANGER = 'd'
	INFORM = 'i'

	recipient = models.CharField(max_length=40)
	seen = models.BooleanField(default=False)
	objects = InheritanceManager()
	state = ""

	def send_mail(self):
		mail_body = self.get_mail_text()
		email = EmailMultiAlternatives(subject=self.get_subj(), body=mail_body, 
			from_email='info@meetme.ir', to=[self.recipient], cc=[], bcc=[],)
		email.send()

	def get_mail_text(self):
		pass

	def get_msg(self):
		pass

	def get_subj(self):
		pass

	def mark_as_seen(self):
		self.seen = True
		self.save()

	def save(self, *args, **kwargs):
		super(Notification, self).save(*args, **kwargs)
		self.send_mail()



class CustomNotification(Notification):
	state = Notification.INFORM
	msg_body = models.TextField()
	mail_body =  models.TextField()
	subject = models.TextField()

	def get_mail_text(self):
		return self.mail_body
		
	def get_msg(self):
		return self.msg_body

	def get_subj(self):
		return self.subject


class InformReservationNotification(Notification):
	state = Notification.INFORM
	reservation = models.ForeignKey(Reservation)

	def get_mail_text(self):
		translated_msg = _("Reservation made %(event)s  in room %(room)s.") \
			%{"event": unicode(self.reservation.interval),
			  "room": self.reservation.room.name }
		mail_body = u"%s" %translated_msg
		return mail_body
		
	def get_msg(self):
		translated_msg = _("Reservation made %(event)s  in room %(room)s.") \
			%{"event": unicode(self.reservation.interval),
			  "room": self.reservation.room.name }
		mail_body = u"%s" %translated_msg
		return translated_msg

	def get_subj(self):
		return u"%s" %_("Reservation made")

	def save(self, *args, **kwargs):
		self.recipient = self.reservation.interval.event.creator.email
		super(InformReservationNotification, self).save(*args, **kwargs)


class InformNoRoomNotification(Notification):
	state = Notification.DANGER
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = _("Reservation cannot be made for meeting %s, since there is no room available at any feasible time. Please perform revote.") % self.meeting.title

		return u"%s" %mail_body
		
	def get_msg(self):
		msg_body = _("Reservation cannot be made for meeting %s, since there is no room available at any feasible time. Please perform revote.") % self.meeting.title

		return u"%s" %msg_body

	def get_subj(self):
		return u"%s" %_("No Room Available")

	def save(self, *args, **kwargs):
		self.recipient = self.meeting.creator.email
		super(InformNoRoomNotification, self).save(*args, **kwargs)


class InformConfirmToGuestsNotification(Notification):
	state = Notification.INFORM
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = _("Reservation %(interval)s that you were invited to, is confirmed by admin, in room %(room)s. We'll be glad if you come!")\
		% {
			"interval": unicode(self.meeting.reservation.interval),
			"room": u"%s" %self.meeting.reservation.room.name
			}
		return u"%s" %mail_body

	def get_msg(self):
		msg_body = _("Reservation %(interval)s that you were invited to, is confirmed by admin, in room %(room)s. We'll be glad if you come!")\
		% {
			"interval": unicode(self.meeting.reservation.interval),
			"room": u"%s" %self.meeting.reservation.room.name
			}
		return u"%s" %msg_body

	def get_subj(self):
		return _("Meeting Confirmed")


class InformConfirmToCreatorNotification(Notification):
	state = Notification.INFORM
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = _("Reservation %(interval)s that you had created, is confirmed by admin, and will be held in room %(room)s. Guests have also been informed.")\
		%{
		"interval": unicode(self.meeting.reservation.interval),
		"room": u"%s" %self.meeting.reservation.room.name
		}
		return u"%s" %mail_body
		
	def get_msg(self):
		msg_body = _("Reservation %(interval)s that you had created, is confirmed by admin, and will be held in room %(room)s. Guests have also been informed.")\
		%{
		"interval": unicode(self.meeting.reservation.interval),
		"room": u"%s" %self.meeting.reservation.room.name
		}
		return u"%s" %msg_body

	def get_subj(self):
		return u"%s" %_("Meeting Confirmed")

	def save(self, *args, **kwargs):
		self.recipient = self.meeting.creator.email
		super(InformConfirmToCreatorNotification, self).save(*args, **kwargs)


class InformCancelToGuestsNotification(Notification):
	state = Notification.DANGER
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = _("Reservation for meeting %s that you were invited to, is cancelled by admin. There might be an edit and revote for which you'll be informed again.") %self.meeting.title 
		return u"%s" %mail_body
		
	def get_msg(self):
		msg_body = _("Reservation for meeting %s that you were invited to, is cancelled by admin. There might be an edit and revote for which you'll be informed again.") %self.meeting.title 
		return u"%s" %msg_body

	def get_subj(self):
		return u"%s" %_("Meeting Cancelled")


class InformCancelToCreatorNotification(Notification):
	state = Notification.DANGER
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = _("Reservation for meeting %s you had created, is cancelled by admin. You can edit it and perform a revote.") %self.meeting.title
		return u"%s" %mail_body
		
	def get_msg(self):
		msg_body = _("Reservation for meeting %s you had created, is cancelled by admin. You can edit it and perform a revote.") %self.meeting.title
		return u"%s" %msg_body

	def get_subj(self):
		return u"%s" %_("Meeting Cancelled")

	def save(self, *args, **kwargs):
		self.recipient = self.meeting.creator.email
		super(InformCancelToCreatorNotification, self).save(*args, **kwargs)

class InvitedNotification(Notification):
	state = Notification.INFORM
	event = models.ForeignKey(Event)

	def get_mail_text(self):
		creator = self.event.creator
		user_id = (creator.first_name + " " + creator.last_name) if creator.last_name else self.event.creator.username
		mail_body = _("You are invited to a meeting named: %(title)s, created by: %(creator)s. You can learn more about and vote on your events, on your 'view events' page.")\
		%{ "title": self.event.title, "creator": user_id

		} 
		return u"%s" % mail_body
		
	def get_msg(self):
		creator = self.event.creator
		user_id = (creator.first_name + " " + creator.last_name) if creator.last_name else self.event.creator.username
		msg_body = _("You are invited to a meeting named: %(title)s, created by: %(creator)s. You can learn more about and vote on your events, on your 'view events' page.") %{ 
		"title": self.event.title, "creator": user_id
		} 
		return u"%s" %msg_body

	def get_subj(self):
		return _("Invitation")


class RevoteNotification(Notification):
	state = Notification.INFORM
	event = models.ForeignKey(Event)

	def get_mail_text(self):
		mail_body = _("There has been a revote for event named: %s. Please cast your vote again.") %self.event.title
		return u"%s" % mail_body

	def get_msg(self):
		msg_body = _("There has been a revote for event named: %s. Please cast your vote again.") %self.event.title
		return u"%s" %msg_body

	def get_subj(self):
		return _("Revote Performed")


class InviteToMeetMeNotification(Notification):
	state = Notification.INFORM

	def get_mail_text(self):
		mail_body = _("You are invited to MeetMe, a website to perform meetings among people and vote for the best time. An account is created for you automatically with username=your_email(%(email)s). You can login using your gmail. Visit us on 'meetme.ir'.")%{"email": self.recipient, }
		return u"%s" % mail_body

	def get_msg(self):
		msg_body = _("Welcome to MeetMe. You can create new events or vote on the events you're invited to easily.")
		return u"%s" % msg_body

	def get_subj(self):
		return _("Invitation To MeetMe")


def inform_revote(event):
	guests = event.guest_list.all()
	for guest in guests:
		notif = RevoteNotification()
		notif.recipient = guest.email
		notif.event = event
		notif.save()

def invite_guests(event):
	guests = event.guest_list.all()
	for guest in guests:
		notif = InvitedNotification()
		notif.recipient = guest.email
		notif.event = event
		notif.save()


def invite_new_guests(l):
	user_emails = User.objects.filter(email__in=l).values_list("email", flat=True)
	new_emails = [email for email in l if email not in user_emails]
	for email in new_emails:
		validate_email(email)
		user = User.objects.create_user(email, email, 'password')
		user.save()
		notif = InviteToMeetMeNotification()
		notif.recipient = email
		notif.save()


def inform_no_room(meeting):
	guests = meeting.guest_list.all()
	for guest in guests:
		notif = InformNoRoomNotification()
		notif.recipient = guest.email
		notif.meeting = meeting
		notif.save()
	notif = InformNoRoomNotification()
	notif.meeting = meeting
	notif.recipient = meeting.creator
	notif.save()


def inform_confirm(meeting):
	guests = meeting.guest_list.all()
	for guest in guests:
		notif = InformConfirmToGuestsNotification()
		notif.recipient = guest.email
		notif.meeting = meeting
		notif.save()
	notif = InformConfirmToCreatorNotification()
	notif.meeting = meeting
	notif.save()


def inform_cancel(meeting):
	guests = meeting.guest_list.all()
	for guest in guests:
		notif = InformCancelToGuestsNotification()
		notif.recipient = guest.email
		notif.meeting = meeting
		notif.save()
	notif = InformCancelToCreatorNotification()
	notif.meeting = meeting
	notif.save()

def inform_reservation(reservation):
	admins = User.objects.filter(is_superuser=True)
	for admin in admins:
		notif = InformReservationNotification()
		notif.reservation = reservation
		notif.recipient = admin.email
		notif.save()
