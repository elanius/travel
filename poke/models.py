from django.db import models

class Person(models.Model):
	name = models.CharField(max_length=200)
	link = models.CharField(max_length=200)

	def __unicode__(self):
		return self.name

class Route(models.Model):
	person = models.ForeignKey(Person)
	date = models.DateField('route date')
	count = models.IntegerField(default=0)

	def __unicode__(self):
		return u'%s' % self.date