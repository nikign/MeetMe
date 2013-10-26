
from django.test import TestCase
from meet.models import *

class SimpleTest2(TestCase):
	fixtures = ['test.json', ]
	def test_basic_addition(self):
		"""
		Tests that 1 + 1 always equals 2.
		"""
		i = Interval.objects.all()
		print i
		self.assertEqual(1 + 1, 2)
