from django.test import TestCase
from meet.notification import *

class NotificationTest(TestCase):
	fixtures = ['test_notification.json', ]
	# TODO: use Interval Mock
	def test_custom_notif(self):
		notif =  CustomNotification()
		notif.msg_body = "test"
		notif.mail_bodt = "test"
		notif.subject = "test"
		notif.save() # get mail text and subject are tested here
		notif.get_msg()

	def test_reservation_notif(self):
		reservation = Reservation.objects.all()[0]
		inform_reservation(reservation) # mail and save and subject tested here
		notif = InformReservationNotification.objects.all()[0]
		notif.get_msg()

	def test_no_room_notif(self):
		meeting = Meeting.objects.all()[0]
		inform_no_room(meeting)
		notif = InformNoRoomNotification.objects.all()[0]
		notif.get_msg()

	def test_confirm_notif(self):
		meeting = Meeting.objects.get(id=1)
		inform_confirm(meeting)
		notif1 = InformConfirmToGuestsNotification.objects.all()[0]
		notif1.get_msg()
		notif2 = InformConfirmToCreatorNotification.objects.all()[0]
		notif2.get_msg()

	def test_cancel_notif(self):
		meeting = Meeting.objects.all()[0]
		inform_cancel(meeting)
		notif1 = InformCancelToGuestsNotification.objects.all()[0]
		notif1.get_msg()
		notif2 = InformCancelToCreatorNotification.objects.all()[0]
		notif2.get_msg()

	def test_invite_guests_notif(self):
		event = Event.objects.all()[0]
		invite_guests(event)
		notif = InvitedNotification.objects.all()[0]
		notif.get_msg()

	def test_revote_notif(self):
		event = Event.objects.all()[0]
		inform_revote(event)
		notif = RevoteNotification.objects.all()[0]
		notif.get_msg()

	def test_invite_new_notif(self):
		guests_list = ['niki.hp2007@gmail.com', 'ashkan.dant3@gmail.com', 'folan.bahman@gmail.com']
		invite_new_guests(guests_list)
		l = InviteToMeetMeNotification.objects.count()
		notif = InviteToMeetMeNotification.objects.all()[0]
		notif.get_msg()
		self.assertEqual(l, 1, "invitation isn't created in the right time")
		try:
			u = User.objects.get(email='folan.bahman@gmail.com')
		except:
			self.assertEqual(True, False, "new user isn't create")