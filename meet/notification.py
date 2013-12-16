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


class InformReservation(Notification):
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


class InformNoRoom(Notification):
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
        super(InformReservation, self).save(*args, **kwargs)
        self.send_mail()
