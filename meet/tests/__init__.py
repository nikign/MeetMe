from django.conf import settings
import unittest


# Used by jenkins
def suite():
    return unittest.TestLoader().discover("meet.tests", pattern="*.py")
