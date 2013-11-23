from django.conf.urls import patterns, include, url

from poke import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home, name='home'),
    url(r'^week_order/(?P<user_id>\w+)/$', views.week_order, name='week_order'),
    url(r'^summary/(?P<user_id>\w+)/$', views.person_summary, name='person_summary'),
    # url(r'^travel/', include('travel.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

