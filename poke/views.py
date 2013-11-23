from django.shortcuts import render
from poke.models import Route, Pasanger, Ticket
import datetime

current_year = 2013

def get_week_days(week_number, year):
	monday = datetime.datetime.strptime('%04d-%02d-1' % (year, week_number-1), '%Y-%W-%w')

	days = list()
	for x in xrange(0,5):
		day_date =  monday+datetime.timedelta(days=x)
		days.append(day_date)

	return days


def get_week_number():
	now = datetime.datetime.now()

	if now.weekday() < 5:
		week_number = now.isocalendar()[1]
	else:
		week_number = now.isocalendar()[1] + 1

	return week_number


def get_year_number():
	return datetime.datetime.now().year


def create_routes(weeks, year):
	cur_week = get_week_number()

	for x in xrange(weeks):
		days_in_week = get_week_days(cur_week+x, current_year)

		for day in days_in_week:
			route = Route(date=day)
			route.save()


def get_week_routes():
	routes = list()

	days = get_week_days(get_week_number(), current_year)
	for day in days:
		routes.append(Route.objects.get(date=day))

	return routes

class RoutePasangers:
	def __init__(self, route, pasangers):
		self.date = route.date
		self.space = route.space
		self.free_space = self.space - len(pasangers)
		self.pasangers = pasangers


def home(request):
	route_pasangers = list()
	for r in get_week_routes():
		pasangers = [t.pasanger for t in Ticket.objects.filter(routes=r)]
		route_pasangers.append(RoutePasangers(r, pasangers))

	context = {
		'curr_date': datetime.datetime.now(),
		'routes': route_pasangers,
	}

	return render(request, 'home.html', context)


def week_order(request, user_id):
	p = Pasanger.objects.get(link=user_id)

	order_placed = place_order(request, p)

	context = {
		'curr_date': datetime.datetime.now(),
		'tickets': get_tickets(p),
		'week_number': get_week_number(),
		'year_number': get_year_number(),
		'traveler': p.name,
		'user_id' : user_id,
		'order_placed': order_placed,
	}

	return render(request, 'week_order.html', context)


def place_order(request, pasanger):
	if len(request.GET) > 0:

		days = get_week_days(int(request.GET.get('week_number')), int(request.GET.get('year_number')))

		for x in xrange(1,6):
			day_id = "day_%d" % x
			reserved = int(request.GET.get(day_id, '0'))

			route = Route.objects.get(date=days[x-1])

			if reserved:
				Ticket.objects.get_or_create(pasanger=pasanger, routes=route)
			else:
				try:
					t = Ticket.objects.get(pasanger=pasanger, routes=route)
					t.delete()
				except Ticket.DoesNotExist:
					pass

		return True

	else:
		return False


def person_summary(request, user_id):
	p = Pasanger.objects.get(link=user_id)

	context = {
		'curr_date': datetime.datetime.now(),
		'user_id' : user_id,
		'routes': [t.routes for t in Ticket.objects.filter(pasanger=p)],
	}

	return render(request, 'person_summary.html', context)


class TripTicket:
	def __init__(self, date, enabled, bought):
		self.date = date
		self.enabled = enabled
		self.bought = bought


def get_tickets(pasanger):
	tickets = list()
	routes = get_week_routes();

	for r in routes:
		try:
			Ticket.objects.get(pasanger=pasanger, routes=r)
			bought = True
		except Ticket.DoesNotExist:
			bought = False

		enabled = True if r.space > 0 else False

		tickets.append(TripTicket(r.date, enabled, bought))

	return tickets
