from django.shortcuts import render
from poke.models import Person, Route
import datetime

def get_week_days(user):
	now = datetime.datetime.now()

	if now.weekday() < 5:
		monday = now - datetime.timedelta(days=now.weekday())
	else:
		monday = now + datetime.timedelta(days=(7 - now.weekday()))

	days = list()
	for x in xrange(0,5):
		day_id = 'day_%d' % x
		day_date =  monday+datetime.timedelta(days=x)
		checked = False

		try:
			r = Route.objects.get(person=user, date=day_date.date())
			if r.count > 0:
				checked = True
		except Route.DoesNotExist:
			pass

		days.append( (day_id, day_date, checked) )

	return days


def get_week_number():
	now = datetime.datetime.now()

	if now.weekday() < 5:
		week_number = now.isocalendar()[1]
	else:
		week_number = now.isocalendar()[1] + 1

	return week_number


def add_to_db(request, user_id):
	user = Person.objects.get(link=user_id)
	week_number = int(request.GET.get('week_number', '-'))
	monday = datetime.datetime.strptime('%04d-%02d' % (2013, week_number), '%Y-%W')

	for x in xrange(1,6):
		day = monday + datetime.timedelta(days=x)

		count = int(request.GET.get('day_%d' % x, '0'))

		try:
			r = Route.objects.get(person=user, date=day.date())
			r.count = count
			r.save()
		except Route.DoesNotExist:
			if count > 0:
				r = Route.objects.create(person=user, date=day.date(), count=count)
		

def home(request):
	context = {}
	return render(request, 'home.html', context)


def person_summary(request, user_id):
	user = Person.objects.get(link=user_id)
	
	if len(request.GET) > 0:
		add_to_db(request, user_id)

	routes = Route.objects.all()

	context = {
		'routes': routes,
		'traveler': user.name,
		'user_id' : user_id,
	}

	return render(request, 'person_summary.html', context)


def week_order(request, user_id):
	p = Person.objects.get(link=user_id)

	context = {
		'days': get_week_days(p),
		'week_number': get_week_number(),
		'traveler': p.name,
		'user_id' : user_id,
	}

	return render(request, 'week_order.html', context)
