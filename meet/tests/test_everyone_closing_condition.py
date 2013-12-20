from django.test import TestCase
from meet.models import *

class ECCTest(TestCase):
	fixtures = ['test_closing_cons.json', ]

	def test(self):
		"""
		Tests get_feasible_intervals_in_order
		"""
		condition = EveryoneClosingCondition.objects.get(pk=3)
		ls = condition.get_feasible_intervals_in_order()
		self.assertEqual(len(ls), 2)
		self.assertEqual(ls[0].id, 5)
		self.assertEqual(ls[1].id, 6)
		condition = EveryoneClosingCondition.objects.get(pk=6)
		ls = condition.get_feasible_intervals_in_order()
		self.assertEqual(len(ls), 0)
		condition = EveryoneClosingCondition.objects.get(pk=7)
		ls = condition.get_feasible_intervals_in_order()
		self.assertEqual(len(ls), 0)
		condition = EveryoneClosingCondition.objects.get(pk=8)
		ls = condition.get_feasible_intervals_in_order()
		self.assertEqual(len(ls), 0)

