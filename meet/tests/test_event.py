from django.test import TestCase
from meet.models import *

class EventTest(TestCase):
	fixtures = ['test_event.json', ]

	def test_user_voted(self):
		"""
		Tests that user_voted.
		"""
		event = Event.objects.all()[0]
		users = User.objects
		self.assertTrue(event.has_user_voted(users.get(pk=2)))
		self.assertTrue(event.has_user_voted(users.get(pk=3)))
		self.assertFalse(event.has_user_voted(users.get(pk=1)))

	def test_get_guest_emails(self):
		"""
		Is mails for guests come correct at hand?
		"""
		event = Event.objects.all()[0]
		ls = event.get_guest_emails()
		self.assertEquals(len(ls),2)
		self.assertTrue("niki.hp2007@gmail.com" in ls)
		self.assertTrue("mehman@ut.ac.ir" in ls)

	def test_get_creator_emails(self):
		"""
		Is mails for guests come correct at hand?
		"""
		event = Event.objects.all()[0]
		email = event.get_creator_email()
		self.assertEquals("ashkan.dant3@gmail.com" ,email)

