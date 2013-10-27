from meet.models import Notification 
from django.core.mail import EmailMultiAlternatives
from MeetMe.settings import ADMIN_MAILS

def inform_admin_reservation(reservation):
	notification = Notification()
	notification.category = Notification.ASK_CONFIRMATION
	notification.event = reservation.interval.event
	notification.save()
	mail_body = "Reservation made for event " + reservation.interval.event + reservation.interval +\
	 " in room " + reservation.room
	email = EmailMultiAlternatives(subject='reservation_made', body=mail_body, 
		from_email='info@meetme.ir', to=ADMIN_MAILS, cc=None, bcc=None,)
	email.send()
	
def inform_no_room_to_owner(meeting):
	notification = Notification()
	notification.category = Notification.NO_ROOM
	notification.event = meeting
	notification.save()
	mail_body = "There is no room available for your meeting \"" + meeting.title + "\".\n please perform a revote."
	email = EmailMultiAlternatives(subject='please perform revote', body=mail_body, 
		from_email='info@meetme.ir', to=[meeting.creator.email], cc=None, bcc=None,)
	email.send()
