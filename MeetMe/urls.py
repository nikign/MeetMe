from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
# from meet.views import create_wizard

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # (r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^$', 'meet.views.home', name='home'),
    # url(r'^MeetMe/', include('MeetMe.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^create/', create_wizard , name='create'),
    url(r'^event/(?P<event_id>\d+)/view' , 'meet.views.view' , name='view'),
    url(r'^meeting/(?P<meeting_id>\d+)/confirm/$', 'meet.views.confirm_meeting', name='confirm'),
    url(r'^meeting/(?P<meeting_id>\d+)/cancel/$', 'meet.views.cancel_meeting', name='cancel'),
    url(r'^admin_review/$' , 'meet.views.admin_review' , name='close'),
    url(r'^user/events/$' , 'meet.views.related_events' , name='related_events'),
    url(r'^event/vote' , 'meet.views.vote' , name='vote'),
    # url(r'^create2/', 'meet.views.create' , name='create'),
    url(r'^google/login/$', 'django_openid_auth.views.login_begin', name='openid-login'),
    url(r'^google/login-complete/$', 'django_openid_auth.views.login_complete', name='openid-complete'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/',}, name='logout'),
    url(r'^tzset/$', 'meet.views.set_timezone' , name='set_timezone'),
    url(r'^create/', 'meet.views.create_wizard' , name='create'),
    

    # url(r'^fakelogin/', 'meet.test_utils.views.fake_login' , name='fake_login'),
)
