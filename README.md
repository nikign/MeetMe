#MeetMe Web Application
This Django based web application helps you arrange meetings among people and find a suitable time for the majority. Also gives you some more advanced options like choosing important guests. You just create the meeting, invite your guests, add options for them to choose between, and give them a deadline to decide whether or not that time is good for them. After the deadline reaches or all the guests decide, the system automatically chooses the best time if possible, reserves a room for the meeting, and informs the guests.  If no suitable time is found, the owner will be informed and asked for a change in options and a revote. An automatic email will be sent to the guests whenever thay are added to a meeting; or a meeting related to them has changed, confirmed or cancelled. 



*Installed libraries:*
==================================================
 - django_jenkins

 - django_openid_auth

 - django-model-utils 

 - pytz

Compatibility issues:
==================================================

 - code is now tested and works fine on django 1.5.5, migration to django 1.6 failed in login through google.


