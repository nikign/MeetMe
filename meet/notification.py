from django.db import models
from django.contrib.contenttypes.models import ContentType
from model_utils.managers import InheritanceManager
from django.utils.translation import ugettext_lazy as _
from meet.models import *
from django.core.mail import EmailMultiAlternatives

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


class CustomNotification(Notification):
	state = Notification.INFORM
	msg_body = models.TextField()
	mail_body =  models.TextField()
	subject = models.TextField()

	def get_mail_text(self):
		return mail_body
		
	def get_msg(self):
		return msg_body

	def get_subj(self):
		return self.subject
	# def save(self, *args, **kwargs):
 #		super(InformReservation, self).save(*args, **kwargs)
 #		self.send_mail()


class InformReservationNotification(Notification):
	state = Notification.INFORM
	reservation = models.ForeignKey(Reservation)

	def get_mail_text(self):
		translated_msg = _("Reservation made for event %s  in room %s." % (unicode(self.reservation.interval), self.reservation.room.name) )
		mail_body = u"%s" %translated_msg
		return mail_body
		
	def get_msg(self):
		translated_msg = _("Reservation made for event %s  in room %s." % (unicode(self.reservation.interval), self.reservation.room.name) )
		msg_body = u"%s" %translated_msg
		print "folen: ", translated_msg
		return translated_msg

	def get_subj(self):
		return _("Reservation made")

	def save(self, *args, **kwargs):
		self.recipient = self.reservation.interval.event.creator.email
		super(InformReservationNotification, self).save(*args, **kwargs)
		self.send_mail()


class InformNoRoomNotification(Notification):
	state = Notification.DANGER
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = u"Reservation cannot be made for meeting " + self.meeting.title +\
		" since there is no room available at any feasible time. Please perform revote."
		return mail_body
		
	def get_msg(self):
		msg_body = u"Reservation cannot be made for meeting " + self.meeting.title +\
		" since there is no room available at any feasible time. Please perform revote."
		return msg_body

	def get_subj(self):
		return "No Room Available"

	def save(self, *args, **kwargs):
		self.recipient = self.meeting.creator.email
		super(InformNoRoomNotification, self).save(*args, **kwargs)
		self.send_mail()


class InformConfirmToGuestsNotification(Notification):
	state = Notification.INFORM
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		msg_body = u"Reservation for meeting you were invited to: " + self.meeting.title +\
		", is confirmed by admin for time interval "+ unicode(self.meeting.reservation.interval) + ", in room " \
		 + self.meeting.reservation.room.name + ". We'll be glad if you come!"
		
	def get_msg(self):
		msg_body = u"Reservation for meeting you were invited to: " + self.meeting.title +\
		", is confirmed by admin for time interval "+ unicode(self.meeting.reservation.interval) + ", in room " \
		 + self.meeting.reservation.room.name + ". We'll be glad if you come!"
		return msg_body

	def get_subj(self):
		return "Meeting Confirmed"

	def save(self, *args, **kwargs):
		super(InformConfirmToGuestsNotification, self).save(*args, **kwargs)
		self.send_mail()

class InformConfirmToCreatorNotification(Notification):
	state = Notification.INFORM
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = u"Reservation for meeting you had created: " + self.meeting.title +\
		", is confirmed by admin for time interval "+ unicode(self.meeting.reservation.interval) + ", in room " \
		 + self.meeting.reservation.room.name + ". Guests have also recieved emails and been informed."
		return mail_body
		
	def get_msg(self):
		msg_body = u"Reservation for meeting you had created: " + self.meeting.title +\
		", is confirmed by admin for time interval "+ unicode(self.meeting.reservation.interval) + ", in room "\
		 + self.meeting.reservation.room.name + ". Guests have also recieved emails and been informed."
		return msg_body

	def get_subj(self):
		return "Meeting Confirmed"

	def save(self, *args, **kwargs):
		self.recipient = self.meeting.creator.email
		super(InformConfirmToCreatorNotification, self).save(*args, **kwargs)
		self.send_mail()

class InformCancelToGuestsNotification(Notification):
	state = Notification.DANGER
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = u"Reservation for meeting you were invited to: " + self.meeting.title +\
		", is cancelled by admin. There might be an edit and revote for which you'll be informed again."
		return mail_body
		
	def get_msg(self):
		msg_body = u"Reservation for meeting you were invited to: " + self.meeting.title +\
		", is cancelled by admin. There might be an edit and revote for which you'll be informed again."
		return msg_body

	def get_subj(self):
		return "Meeting Cancelled"

	def save(self, *args, **kwargs):
		super(InformCancelToGuestsNotification, self).save(*args, **kwargs)
		self.send_mail()


class InformCancelToCreatorNotification(Notification):
	state = Notification.DANGER
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = u"Reservation for meeting you had created: " + self.meeting.title +\
		", is cancelled by admin. You can edit it and perform a revote."
		return mail_body
		
	def get_msg(self):
		msg_body = u"Reservation for meeting you had created: " + self.meeting.title +\
		", is cancelled by admin. You can edit it and perform a revote."
		return msg_body

	def get_subj(self):
		return "Meeting Cancelled"

	def save(self, *args, **kwargs):
		self.recipient = self.meeting.creator.email
		super(InformCancelToCreatorNotification, self).save(*args, **kwargs)
		self.send_mail()

class InvitedNotification(Notification):
	state = Notification.INFORM
	event = models.ForeignKey(Event)

	def get_mail_text(self):
		creator = self.event.creator
		user_id = (creator.first_name + " " + creator.last_name) if creator.last_name else self.event.creator.username
		mail_body = u"You are invited to a meeting named: " + self.event.title +\
		"created by: " + user_id + \
		". You can learn more about and vote on your events, on your 'view your events' link."
		return mail_body
		
	def get_msg(self):
		creator = self.event.creator
		user_id = (creator.first_name + " " + creator.last_name) if creator.last_name else self.event.creator.username
		msg_body = u"You are invited to a meeting named: " + self.event.title +\
		"created by: " + user_id +\
		 ". You can learn more about and vote on your events, on your 'view your events' link."
		return msg_body

	def get_subj(self):
		return "Invitation"

	def save(self, *args, **kwargs):
		super(InvitedNotification, self).save(*args, **kwargs)
		self.send_mail()
