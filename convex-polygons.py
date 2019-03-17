convex polygons.py
Last year
May 29, 2018
S
You uploaded an item
Text
convex polygons.py

'''
This module contains a set of geometric classes and functions that
are aimed at solving Convex Holes problem #252 at Project Euler.
https://projecteuler.net/problem=252

by Sergey Lisitsin, 2018
sergey.lisitsin@gmail.com

'''


from math import sqrt, pi
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

	def __eq__(self, other):
		return (self.x, self.y) == (other.x, other.y)

	def __lt__(self, other):
		return self.x < other.x

	def __hash__(self):
		return hash(repr(self))



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

		self.halfper = self.perimeter / 2
		self.semisection1 = self.halfper - self.section1.length
		self.semisection2 = self.halfper - self.section2.length
		self.semisection3 = self.halfper - self.section3.length
		if (self.halfper * self.semisection1 * self.semisection2 * self.semisection3) > 0:
			self.area = sqrt(self.halfper * self.semisection1 * self.semisection2 * self.semisection3)
		else:
			self.area = 0


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
		self.toparea = 0
		self.bottomarea = 0
		self.sections = []
		self.area = 0
		self.rbound = self.points[-1].x
		self.lbound = self.points[0].x
		self.tbound = sorted(points, key = lambda x: x.y)[-1]
		self.bbound = sorted(points, key = lambda x: x.y)[0]


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

		self.overarch = set(self.overarch)
		self.underarch = set(self.underarch)

		self.overarch = list(self.overarch)
		self.underarch = list(self.underarch)

		
		self.overarch = sorted(self.overarch, key = lambda x: (x.x, x.y))
		self.underarch = sorted(self.underarch, key = lambda x: (x.x, x.y))

		for p in n_grams(self.overarch, 2):
			self.sections.append(Section(p[0],p[1]))
		for p in n_grams(self.underarch, 2):
			self.sections.append(Section(p[0],p[1]))

		
		# Building a list of triangles above the equator line
		for p in n_grams(self.overarch[1::], 2):
			self.toptriangles.append(Triangle(self.overarch[0], *p))
		# Building a list of triangles below the equator line
		for p in n_grams(self.underarch[1::], 2):
			self.bottomtriangles.append(Triangle(self.underarch[0], *p))
		# Calculating the top triangles combined area
		for t in self.toptriangles:
			self.toparea  = self.toparea + t.area
		# Calculating the bottom triangles combined area
		for t in self.bottomtriangles:
			self.bottomarea = self.bottomarea + t.area
		self.area = self.toparea + self.bottomarea


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


def isinside(t: Triangle, point: Point):
	''' This function finds out whether the point is
	inside of a given triangle's perimeter '''

	if point.x == t.a.x and point.y == t.a.y:
		return False
	if point.x == t.b.x and point.y == t.b.y:
		return False
	if point.x == t.c.x and point.y == t.c.y:
		return False
	if not istriangle(point, t.a, t.b):
		return False
	if not istriangle(point, t.b, t.c):
		return False
	if not istriangle(point, t.a, t.c):
		return False

	sub1 = Triangle(point, t.a, t.b)
	sub2 = Triangle(point, t.b, t.c)
	sub3 = Triangle(point, t.a, t.c)

	if (round(sub1.area, 2) + round(sub2.area, 2) + \
		round(sub3.area, 2)) > round(t.area, 2):
		return False	
	else:
		return True




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

def n_grams(a, n):
	''' this function creates a sliding window of length "n"
	over a list "a".'''
	z = (islice(a, i, None) for i in range(n))
	return zip(*z)


def isconvex(p: Polygon):
	topsections = []
	bottomsections = []
	for s in p.sections:
		sidea = []
		sideb = []
		for pnt in p.points:
			if pnt == s.a or pnt == s.b:
				continue
			crosspoint = pnt.x * s.slope + s.rais
			if crosspoint < pnt.y:
				sidea.append(pnt)
			if crosspoint > pnt.y:
				sideb.append(pnt)
			if len(sidea) > 0 and len(sideb) > 0:
				return False
	return True


def isempty(pol: Polygon, pts):
	for p in pts:
		for t in pol.toptriangles:
			if isinside(t, p):
				return False
		for t in pol.bottomtriangles:
			if isinside(t, p):
				return False
	return True



def mybestarea(base: Section, points):
	baseleft = base.a.x
	baseright = base.b.x
	topsubset = list(filter(lambda x: (x.x > baseleft and x.x < baseright and \
	Section(base.a, x).slope > base.slope), points))
	bottomsubset = list(filter(lambda x: (x.x > baseleft and x.x < baseright and \
	Section(base.a, x).slope < base.slope), points))
	emptypots = []

	# if len(topsubset) > 0:
	# 	for x in topsubset:
	# 		currenttriangle = Triangle(base.a, x, base.b)
	# 		empty = True
	# 		for p in topsubset:
	# 			if isinside(currenttriangle, p):
	# 				empty = False
	# 		if empty:
	# 			emptypots.append(x)

	# if len(bottomsubset) > 0:
	# 	for x in bottomsubset:
	# 		currenttriangle = Triangle(base.a, x, base.b)
	# 		empty = True
	# 		for p in bottomsubset:
	# 			if isinside(currenttriangle, p):
	# 				empty = False
	# 		if empty:
	# 			emptypots.append(x)
	
	if len(topsubset) > 0:
		topsubset = sorted(topsubset, key = lambda x: x.y)
		for x in range (0, len(topsubset)-1):
			currenttriangle = Triangle(base.a, topsubset[x+1], base.b)
			if not isinside(currenttriangle, topsubset[x]):
				emptypots.append(topsubset[x])
			else:
				break
	if len(bottomsubset) > 0:
		bottomsubset = sorted(bottomsubset, key = lambda x: x.y, reverse=True)
		for x in range (0, len(bottomsubset)-1):
			currenttriangle = Triangle(base.a, bottomsubset[x+1], base.b)
			if not isinside(currenttriangle, bottomsubset[x]):
				emptypots.append(bottomsubset[x])
			else:
				break


	if len(emptypots) >  1:
		emptypots.append(base.a)
		emptypots.append(base.b)
		#print(emptypots)
		currentpolygon = Polygon(emptypots)
		if base.a.x == -665 and base.b.x == 913:
				print ("Current base is {} - {}".format(base.a, base.b))
				print ("current top subset is {}".format(topsubset))
				print ("current bottom subset is {}".format(bottomsubset))
				print ("current area is {}".format(currentpolygon.area))
				for t in currentpolygon.toptriangles:
					print( t.a, t.b, t.c)
				for t in currentpolygon.bottomtriangles:
					print( t.a, t.b, t.c)
		#print ("current points are: {}".format(currentpolygon.points))
		if isconvex(currentpolygon):
			return currentpolygon.area
	return 0



'''
S0 = 290797
Sn+1 = Sn^2 mod 50515093
Tn = (Sn mod 2000 ) - 1000
Sn - pseudo random sequence of numbers
Tn is the next number in the point coordinate list derived from Sn sequence
'''

points = []
ssec = []
ssec.append((290797 * 290797) % 50515093)

for s in range(1000):
	cur = ssec[-1] * ssec[-1]
	curmod = cur % 50515093
	ssec.append(curmod)

for s in ssec:
	points.append(s % 2000)

group_adjacent = lambda a, k: zip(*([iter(a)] * k))


pts = []
for x in group_adjacent(points, 2):
	pts.append(Point(str(x), *(list(x))))

areas = []
for pt in range(len(pts)):
	for pt2 in range(pt,len(pts)):
		print("current section is {} - {} ".format(pts[pt], pts[pt2]))
		areas.append(mybestarea(Section(pts[pt],pts[pt2]), pts))

