from django.test import TestCase
from meet.models import *

class HCCTest(TestCase):
	fixtures = ['test_closing_cons.json', ]

	def test(self):
		"""
		Tests get_feasible_intervals_in_order
		"""
		condition = HalfAtLeastClosingCondition.objects.get(pk=4)
		ls = condition.get_feasible_intervals_in_order()
		self.assertEqual(len(ls), 2)
		self.assertEqual(ls[0].id, 8)
		self.assertEqual(ls[1].id, 9)
		condition = HalfAtLeastClosingCondition.objects.get(pk=9)
		ls = condition.get_feasible_intervals_in_order()
		self.assertEqual(len(ls), 1)
		self.assertEqual(ls[0].id, 20)
		condition = HalfAtLeastClosingCondition.objects.get(pk=10)
		ls = condition.get_feasible_intervals_in_order()
		self.assertEqual(len(ls), 0)

