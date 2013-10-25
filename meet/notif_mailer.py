
def create_notif():
	pass
	# TODO

def send_mail (notif):
	pass 
	# TODO

def send_test_mail(request):
	from django.core.mail import EmailMultiAlternatives

	email = EmailMultiAlternatives(subject='Test Mail', body="ma khe'li khafanim", 
		from_email='info@meetme.ir', to=['niki.hp2007@gmail.com'], cc=['ashkan.dant3@gmail.com'], bcc=None,)
	# email.attach_alternative(body_html, "text/html")
	email.send()
	print "hasan o jafar o abbas o ali"

	return render_to_response('event_saved.html', {
		'message' : "Mail zadam.",
		'status' : 'khafan'
	})	
