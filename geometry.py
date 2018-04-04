'''
This module contains a set of geometric classes and functions that
are aimed at solving Convex Holes problem #252 at Project Euler.
https://projecteuler.net/problem=252

by Sergey Lisitsin, 2018
sergey.lisitsin@gmail.com

'''


from math import sqrt
import itertools, collections
from itertools import islice
from random import *



class Point:
	''' A class of objects representing points on plane
	Has two coordinate variables, x and y and a list of
	associated triangles.'''

	def __init__(self, name, x: float, y: float):
		self.name = name
		self.x = x
		self.y = y
		self.mytriangles = set()

	def coordinates(self):
		''' Returns point's coordinates x and y'''
		return self.x, self.y

	def sectozero(self):
		zero = Point(0,0)
		return Section(self,zero)

	def __repr__(self):
		return ('{}: {} {}'.format(self.__class__.__name__, self.x, self.y))



class Section:
	''' A class of objects representing a section. Has
	name, and two point objects, representing the ends of
	a section. Also has length that is calculated'''

	def __init__(self, a: Point, b: Point):
		self.name = a.name + b.name
		self.a = a
		self.b = b
		self.deltax = float(abs(self.b.x - self.a.x))
		self.deltay = float(self.b.y - self.a.y)
		if self.deltax == 0.0 :
			self.slope = 0.0
		else:
			self.slope = (self.deltay)/(self.deltax)			# Finding the slope
		self.rais  = self.a.y-self.a.x*self.slope				# Finding the raise
		hypsqr = (self.deltax*self.deltax)+(self.deltay*self.deltay)
		self.length = sqrt(hypsqr)
		

class Triangle:
	''' A class of objects representing a triangle.
	Consists of three point objects that don't lie
	on the same	line. Has perimeter and area '''

	def __init__(self, a: Point, b: Point, c: Point):
		self.name = a.name + b.name + c.name
		self.adjacents = set()
		self.a = a 										#points and sections of the triangle
		self.b = b 										#
		self.c = c 										#
		self.section1 = Section(self.a,self.b)			#
		self.section2 = Section(self.b,self.c)			#
		self.section3 = Section(self.a,self.c)			#

		if istriangle(self.a, self.b, self.c):
			self.real = True
		else:
			self.real = False

		self.perimeter = self.section1.length + \
		self.section2.length + self.section3.length

		p = self.perimeter / 2
		self.area = sqrt(p *(p -self.section1.length) * \
		(p - self.section2.length) * (p - self.section3.length))

	def returnpoints(self):
		return(self.a, self.b, self.c)
	def returnsections(self):
		return(self.section1, self.section2, self.section3)



class Polygon:
	''' A class of objects representing a polygon.
	Consists of an list of points. Has perimeter
	and area. '''

	def __init__(self, points):

		
		self.points = sorted(points, key = lambda x: (x.x, x.y))
		self.equator = Section(self.points[0], self.points[-1])		
		self.toptriangles = []
		self.bottomtriangles = []
		self.overarch = []
		self.underarch = []
		self.topconvex = True
		self.bottomconvex = True
		self.empty = True
		self.toprays = []
		self.bottomrays = []
		self.toparea = 0
		self.bottomarea = 0
		self.convex = False
		self.area = 0


		''' The following section fills in two lists: list of
		points that belong to the top arch and list of poitns
		that belong to the bottom arch. Each arch also starts
		with the first point of the equator and ends with the 
		second point of the equator, being the two furthest
		points of the entire polygon on X axis.'''

		self.overarch.append(self.equator.a)
		self.underarch.append(self.equator.a)

		for p in self.points:
			if pointbelongs(p, self.equator):
				self.empty = False
		
			if Section(self.equator.a, p).slope > self.equator.slope:
				self.overarch.append(p)
			else:
				self.underarch.append(p)
		
		self.overarch.append(self.equator.b)
		self.underarch.append(self.equator.b)

		self.overarch = list(set(sorted(self.overarch, key = lambda x: (x.x, x.y))))
		self.underarch = list(set(sorted(self.underarch, key = lambda x: (x.x, x.y))))

		if len(self.overarch) > 0:
			for s in (self.overarch[1::]):
				self.toprays.append(Section(self.equator.a,s))

		if len(self.underarch) > 0:
			for s in (self.underarch[1::]):
				self.bottomrays.append(Section(self.equator.a,s))


		if len(self.toprays) > 0:
			for s in n_grams(self.toprays, 2):
				if s[1].b.x == self.equator.b.x and s[1].b.y == self.equator.b.y:
					break
				if not s[1].slope < s[0].slope:
					self.topconvex = False

		if len(self.bottomrays) > 0:
					for s in n_grams(self.bottomrays, 2):
						if s[1].b.x == self.equator.a.x and s[1].b.y == self.equator.b.y:
							break
						if not s[1].slope > s[0].slope:
							self.bottomconvex = False					

		if self.topconvex and self.bottomconvex:
			self.convex = True

		if self.convex == True and self.empty == True:
			for p in n_grams(self.overarch, 3):
				self.toptriangles.append(Triangle(*p))

			for p in n_grams(self.underarch, 3):
				self.bottomtriangles.append(Triangle(*p))

			for t in self.toptriangles:
				self.toparea  = self.toparea + t.area

			for t in self.bottomtriangles:
				self.bottomarea = self.bottomarea + t.area
			if len(self.toptriangles) < 1:
				self.toparea = 0
			if len(self.bottomtriangles) < 1:
				self.bottomarea = 0

			self.area = self.bottomarea + self.toparea






def linefunc(a: Point, b: Point):
	''' This function returns slope and raise for a line
	defined by two points'''
	if a.x == b.x:
		rais = False
		slope = 0

	if a.x < b.x:
		slope = (b.y-a.y)/(b.x-a.x)	# Finding the slope if a is closer to Y axis
		rais  = a.y-a.x*slope		# Finding the raise if a is closer to Y axis
	elif b.x < a.x:
		slope = (a.y-b.y)/(a.x-b.x) # Finding the slope if b is closer to Y axis
		rais = b.y-b.x*slope		# Finding the raise if b is closer to Y axis
	return (slope,rais)



def ifintersect(s1: Section, s2: Section):
	''' This function finds out whether two
	sections intersect. '''
	s1xrange = set(range(s1.a.x, s1.b.x + 1))	#the range of x values in section1 
	s1yrange = set(range(s1.a.y, s1.b.y + 1))	#the range of y values in section1
	s2xrange = set(range(s2.a.x, s2.b.x + 1))	#the range of x values in section2
	s2yrange = set(range(s2.a.y, s2.b.y + 1))	#the range of y values in section2

	xoverlap = s1xrange & s2xrange
	if not xoverlap:
		return False

	s1yoverstart = list(xoverlap)[0] * s1.slope + s1.rais
	s1yoverend   = list(xoverlap)[-1] * s1.slope + s1.rais
	s2yoverstart = list(xoverlap)[0] * s2.slope + s2.rais
	s2yoverend   = list(xoverlap)[-1] * s2.slope + s2.rais

	if s1yoverstart > s2yoverstart and s1yoverend < s2yoverend:
		return True

	if s2yoverstart > s1yoverstart and s2yoverend < s1yoverend:
		return True

	return False

def istriangle(a: Point, b: Point, c: Point):
	''' This function finds out whether all 3
	points lie on the same line, in which case
	they can't form a triangle. It uses linefunc
	to find out whether all 3 points belong to
	the line built by the same function'''

	first = linefunc(a,b)				#function of the first two points
	second = linefunc(b,c)				#function of the second two points
	if first == second:					#if they are the same, then you
		return False					# can't build a triangle with these 3 lines
	else:
		return True


def isinside(t: Triangle, point: Point):
	''' This function finds out whether the point is
	inside of a given triangle's perimeter '''

	if point.x == t.a.x and point.y == t.a.y:
		return False
	if point.x == t.b.x and point.y == t.b.y:
		return False
	if point.x == t.c.x and point.y == t.c.y:
		return False

	sub1 = Triangle(point, t.a, t.b)
	sub2 = Triangle(point, t.b, t.c)
	sub3 = Triangle(point, t.a, t.c)

	if (round(sub1.area, 2) + round(sub2.area, 2) + \
		round(sub3.area, 2)) > round(t.area, 2):
		return False	
	else:
		return True


def pointsmatch(p1: Point, p2: Point):
	if p1.x == p2.x and p1.y == p2.y:
		return True
	else:
		return False

def sectionmatch(s1: Section, s2: Section):
	if s1.a == s2.a and s1.b == s2.b:
	   return True
	return False


def adjnoncross(t1: Triangle, t2: Triangle):
	'''This function finds out if two triangles are
	adjacent and their sides don't cross each other'''

	t1sides = [t1.section1, t1.section2, t1.section3]
	t2sides = [t2.section1, t2.section2, t2.section3]
	t1points = set()
	t2points = set()
	sharedside = False

#######################################################
## This section creates two sets of points, one for  ##
## each triangle. Then third set is an intersection  ##
## of them. If there is more than one common point,  ##
## then the two triangles are adjacent.              ##
#######################################################
	for side1 in t1sides:
		for side2 in t2sides:
			if sectionmatch(side1,side2):
				t1sides.remove(side1)
				t2sides.remove(side2)
				sharedside = side1
	if sharedside == False:
		return False

########################################################
## This section checks if any of the sides of one     ##
## triangles intersect any side of another one. If it ##
## does, then the triangles won't form a convex       ##
## polygon 											  ##
########################################################

	for side1 in t1sides:
		for side2 in t2sides:
			if ifintersect(side1,side2):
				return False
	return True



def filltriangles(points):
	''' This function creates a list of all possible
	triangles'''

	triangles = []
	for t in itertools.combinations(points,3):
		if istriangle(*list(t)):
			triangle = Triangle(*list(t))
			if triangle.real == True:
				triangles.append(triangle)
	return triangles

def filtertriangles(triangles, points):
	''' This function filters out the triangles that are
	not empty, i.e. they have a point positioned inside the
	triangle's perimeter. '''

	for p in points:
		for t in triangles:
			if isinside(t,p):
				triangles.remove(t)
	for t in triangles:
		subs = triangles
		subs.remove(t)
		for sub in subs:
			if set(sub.name) == set(t.name):
				triangles.remove(t)



	return triangles

def fillheads(triangles, points):
	'''This function populates a triangle list for every
	point with triangles that have that point as one of
	the vertices. Takes in list of triangles and list of
	points as two arguments.'''

	for p in points:
		for t in triangles:
			if p in t.returnpoints():
				p.mytriangles.add(t)


def filladjacents(triangle, triangles):
	for t in triangles:
		if adjnoncross(triangle,t):
			triangle.adjacents.add(t)

def sortpoints(points):
	''' This function sorts a list of points by their
	X coordinate in ascending order.'''

def getx(point):
	return point.x

def pointbelongs(p: Point, s: Section):
	''' This function finds out whether a given point
	belongs to a given section. Takes point and section
	as arguments and returns boolean value. '''

	if p.x not in list(range(s.a.x,s.b.x)):
		return False
	newsection = Section(p,s.a)
	if linefunc(s.a, s.b) == linefunc(newsection.a, newsection.b):
		return True
	else:
		return False


def n_grams(a, n):
	''' this function creates a sliding window of length "n"
	over a list "a".'''
	z = (islice(a, i, None) for i in range(n))
	return zip(*z)

def isemptypolygon(pol, points):
	for t in pol.toptriangles:
		for p in points:
			if isinside(t, p):
				return False
	for t in pol.bottomtriangles:
		for p in points:
			if isinside(t, p):
				return False
	return True
