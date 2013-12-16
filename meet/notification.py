from django.db import models
from meet.models import *

class Notification(models.Model):
	recipient = models.ForeignKey(User)
	seen = models.BooleanField(default=False)
	
	def send_mail(self):
		mail_body = self.get_mail_text()
		email = EmailMultiAlternatives(subject='reservation_made', body=mail_body, 
			from_email='info@meetme.ir', to=self.recipient.e_mail, cc=None, bcc=None,)
		email.send()

	def get_mail_text(self):
		pass

	def get_msg(self):
		pass


class CustomNotification(Notification):
	reservation = models.ForeignKey(Reservation)

	def get_mail_text(self):
		mail_body = "Reservation made for event " + self.reservation.interval.event + self.reservation.interval +\
		 " in room " + self.reservation.room + ", created by " + self.reservation.interval.event.creator
		return mail_body
		
	def get_msg(self):
		msg_body = "Reservation made for event " + self.reservation.interval.event + self.reservation.interval +\
		 " in room " + self.reservation.room + ", created by " + self.reservation.interval.event.creator
		return msg_body

	def save(self, *args, **kwargs):
        super(InformReservation, self).save(*args, **kwargs)
        self.send_mail()


class InformReservationNotification(Notification):
	reservation = models.ForeignKey(Reservation)

	def get_mail_text(self):
		mail_body = "Reservation made for event " + self.reservation.interval.event + self.reservation.interval +\
		 " in room " + self.reservation.room + ", created by " + self.reservation.interval.event.creator
		return mail_body
		
	def get_msg(self):
		msg_body = "Reservation made for event " + self.reservation.interval.event + self.reservation.interval +\
		 " in room " + self.reservation.room + ", created by " + self.reservation.interval.event.creator
		return msg_body

	def save(self, *args, **kwargs):
        super(InformReservation, self).save(*args, **kwargs)
        self.send_mail()


class InformNoRoomNotification(Notification):
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = "Reservation cannot be made for meeting " + self.meeting +
		" since there is no room available at any feasible time. Please perform revote."
		return mail_body
		
	def get_msg(self):
		msg_body = "Reservation cannot be made for meeting " + self.meeting +
		" since there is no room available at any feasible time. Please perform revote."
		return msg_body

	def save(self, *args, **kwargs):
        self.recipient = meeting.creator
        super(InformNoRoom, self).save(*args, **kwargs)
        self.send_mail()


class InformConfirmToGuestsNotification(Notification):
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = "Reservation for meeting you were invited to: " + self.meeting +
		", is confirmed by admin for time interval "+ self.meeting.reservation.interval + ", in room " 
		 + self.meeting.reservation.room + ". We'll be glad if you come!"
		return mail_body
		
	def get_msg(self):
		msg_body = "Reservation for meeting you were invited to: " + self.meeting +
		", is confirmed by admin for time interval "+ self.meeting.reservation.interval + ", in room " 
		 + self.meeting.reservation.room + ". We'll be glad if you come!"
		return msg_body

	def save(self, *args, **kwargs):
        super(InformConfirmToGuests, self).save(*args, **kwargs)
        self.send_mail()

class InformConfirmToCreatorNotification(Notification):
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = "Reservation for meeting you had created: " + self.meeting +
		", is confirmed by admin for time interval "+ self.meeting.reservation.interval + ", in room " 
		 + self.meeting.reservation.room + ". Guests have also recieved emails and been informed."
		return mail_body
		
	def get_msg(self):
		mail_body = "Reservation for meeting you had created: " + self.meeting +
		", is confirmed by admin for time interval "+ self.meeting.reservation.interval + ", in room " 
		 + self.meeting.reservation.room + ". Guests have also recieved emails and been informed."
		return msg_body

	def save(self, *args, **kwargs):
        super(InformConfirmToCreator, self).save(*args, **kwargs)
        self.send_mail()

class InformCancelToGuestsNotification(Notification):
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = "Reservation for meeting you were invited to: " + self.meeting +
		", is cancelled by admin. There might be an edit and revote for which you'll be informed again."
		return mail_body
		
	def get_msg(self):
		msg_body = "Reservation for meeting you were invited to: " + self.meeting +
		", is cancelled by admin. There might be an edit and revote for which you'll be informed again."
		return msg_body

	def save(self, *args, **kwargs):
        super(InformCancelToGuests, self).save(*args, **kwargs)
        self.send_mail()


class InformCancelToCreatorNotification(Notification):
	meeting = models.ForeignKey(Meeting)

	def get_mail_text(self):
		mail_body = "Reservation for meeting you had created: " + self.meeting +
		", is cancelled by admin. You can edit it and perform a revote."
		return mail_body
		
	def get_msg(self):
		mail_body = "Reservation for meeting you had created: " + self.meeting +
		", is cancelled by admin. You can edit it and perform a revote."
		return msg_body

	def save(self, *args, **kwargs):
        super(InformCancelToCreator, self).save(*args, **kwargs)
        self.send_mail()
