from django.db import models
from meet.models import *
from django.core.mail import EmailMultiAlternatives
# from django.contrib.auth.models import User

class Notification(models.Model):
	# recipient = models.ForeignKey(User)
	recipient = models.CharField(max_length=40)
	seen = models.BooleanField(default=False)

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


class CustomNotification(Notification):
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
	reservation = models.ForeignKey(Reservation)

	def get_mail_text(self):
		mail_body = u"Reservation made for event "  + unicode(self.reservation.interval)  +\
		 " in room " + self.reservation.room.name
		return mail_body
		
	def get_msg(self):
		msg_body = u"Reservation made for event " +  unicode(self.reservation.interval)  +\
		 " in room " + self.reservation.room.name 
		return msg_body

	def get_subj(self):
		return "Reservation made"

	def save(self, *args, **kwargs):
		self.recipient = self.reservation.interval.meeting.creator.email
		super(InformReservationNotification, self).save(*args, **kwargs)
		self.send_mail()


class InformNoRoomNotification(Notification):
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
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = u"Reservation for meeting you had created: " + self.meeting.title +\
		", is cancelled by admin. You can edit it and perform a revote."
		return mail_body
		
	def get_msg(self):
		mail_body = u"Reservation for meeting you had created: " + self.meeting.title +\
		", is cancelled by admin. You can edit it and perform a revote."
		return msg_body

	def get_subj(self):
		return "Meeting Cancelled"

	def save(self, *args, **kwargs):
		self.recipient = self.meeting.creator.email
		super(InformCancelToCreatorNotification, self).save(*args, **kwargs)
		self.send_mail()

class InvitedNotification(Notification):
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
