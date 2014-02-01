from django.shortcuts import render
from poke.models import Route, Pasanger, Ticket
import datetime

current_year = 2014

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


def create_routes(week_num, year):
	days_in_week = get_week_days(week_num, current_year)

	for day in days_in_week:
		route = Route(date=day)
		route.save()


def get_week_routes(weeks=1):
	routes = list()

	step = 1 if weeks > 0 else -1
	for x in xrange(0, weeks, step):
		week_num = get_week_number()+x
		days = get_week_days(week_num, current_year)
		for day in days:
			try:
				route = Route.objects.get(date=day)
			except Route.DoesNotExist:
				create_routes(week_num, current_year)
				route = Route.objects.get(date=day)

			routes.append(route)

	return routes


class RoutePasangers:
	def __init__(self, route, pasangers):
		self.date = route.date
		self.space = route.space
		self.free_space = self.space - len(pasangers)
		self.pasangers = pasangers


def home(request, user_id=None):
	if user_id != None:
		place_order(request, Pasanger.objects.get(link=user_id))

	route_pasangers = list()
	for r in get_week_routes():
		pasangers = [t.pasanger for t in Ticket.objects.filter(route=r)]
		route_pasangers.append(RoutePasangers(r, pasangers))

	context = {
		'curr_date': datetime.datetime.now(),
		'routes': route_pasangers,
	}

	return render(request, 'home.html', context)


def week_order(request, user_id):
	p = Pasanger.objects.get(link=user_id)

	context = {
		'curr_date': datetime.datetime.now(),
		'tickets': get_tickets(p),
		'week_number': get_week_number(),
		'year_number': get_year_number(),
		'traveler': p.name,
		'user_id' : user_id,
	}

	return render(request, 'week_order.html', context)


def place_order(request, pasanger):
	if len(request.GET) > 0:

		days = get_week_days(int(request.GET.get('week_number')), int(request.GET.get('year_number')))

		for x in xrange(1,6):
			day_id = "day_%d" % x
			day_back = "dayback_%d" % x

			reserved = int(request.GET.get(day_id, '0'))
			reserved_back = int(request.GET.get(day_back, '0'))

			route = Route.objects.get(date=days[x-1])

			if reserved or reserved_back:
				(t, created) = Ticket.objects.get_or_create(pasanger=pasanger, route=route)
				if reserved and reserved_back:
					t.is_return = True
				elif reserved:
					t.is_return = False
				t.save()
			else:
				try:
					t = Ticket.objects.get(pasanger=pasanger, route=route)
					t.delete()
				except Ticket.DoesNotExist:
					pass

		return True

	else:
		return False


def person_summary(request, user_id, month=None):
	p = Pasanger.objects.get(link=user_id)

	curr_date = datetime.datetime.now()

	if month == None:
		month = curr_date.month

	routes = [(t.route, t.is_return) for t in Ticket.objects.filter(pasanger=p, route__date__month=int(month)).order_by('route__date')]

	routes_sum = 0
	for (r, i) in routes:
		if i:
			routes_sum += 2
		else:
			routes_sum += 1

	context = {
		'curr_date': curr_date,
		'curr_month': datetime.datetime(current_year, int(month), 1),
		'months': [datetime.datetime(current_year, x, 1) for x in xrange(1, 13)],
		'user_id': user_id,
		'routes': routes,
		'routes_sum': routes_sum,
	}

	return render(request, 'person_summary.html', context)


class TripTicket:
	def __init__(self, date, enabled, bought, back):
		self.date = date
		self.enabled = enabled
		self.bought = bought
		self.back = back


def get_tickets(pasanger, weeks=1):
	tickets = list()
	routes = get_week_routes(weeks);

	for r in routes:
		try:
			t = Ticket.objects.get(pasanger=pasanger, route=r)
			bought = True
			back = t.is_return
		except Ticket.DoesNotExist:
			bought = False
			back = False

		ticket_count = Ticket.objects.filter(pasanger=pasanger, route=r).count()

		enabled = True if r.space > 0 and ticket_count <= r.space else False

		tickets.append(TripTicket(r.date, enabled, bought, back))

	return tickets


def simple_view(request):
	route_pasangers = list()
	for r in get_week_routes():
		pasangers = [t.pasanger for t in Ticket.objects.filter(route=r)]
		route_pasangers.append(RoutePasangers(r, pasangers))

	context = {
		'curr_date': datetime.datetime.now(),
		'routes': route_pasangers,
	}

	return render(request, 'simple_view.html', context)
