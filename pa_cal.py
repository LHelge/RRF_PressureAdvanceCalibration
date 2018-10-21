# The MIT License (MIT)
#
# Copyright (c) <year> <copyright holders>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from math import pi, cos, sin, sqrt
from pathlib import Path
import datetime

# Class for storing filament properties
class Filament:
	# Filament constructor
	#	Params:
	#		name					Filament name
	#		diameter				Filament diameter [mm]
	# 		extrusion_factor		Extrusion factor [%]
	# 		density					Filament density [g/mm^3]
	# 		bed_temp				Print bed temperature [deg C]
	# 		bed_layer0_temp			First layer bed temperature [deg C]
	# 		hotend_temp				Print hotend temperature [deg c]
	# 		hotend_layer0_temp		First layer hotend temperature [deg C]
	# 		fan_speed				Print fan speed [%]
	# 		fan_layer0_speed		First layer fan speed [%]
	def __init__(self, name, diameter, extrusion_factor, density, bed_temp, bed_layer0_temp, hotend_temp, hotend_layer0_temp, fan_speed, fan_layer0_speed):
		self.name = name
		self.diameter = diameter
		self.extrusion_factor = extrusion_factor / 100
		self.density = density
		self.bed_temp = bed_temp
		self.bed_layer0_temp = bed_layer0_temp
		self.hotend_temp = hotend_temp
		self.hotend_layer0_temp = hotend_layer0_temp
		self.fan_speed = fan_speed
		self.fan_layer0_speed = fan_layer0_speed

# Class for storing printer properties
class Printer:
	# Printer constructor
	#	Params:
	#		name 					Printer name
	# 		delta					Is this printer a delta configuration (put origo in center) [bool]
	#		radius					Print volume radius (only applicable for delta printers) [mm]
	# 		size_x					Print volume size in X-axis 8mm]
	# 		size_y					Print volume size in Y-axis 8mm]
	#		size_z					Print volume size in Z-axis 8mm]
	# 		nozzle					Nozzle size [mm]
	# 		retract_distance		Retraction distance [mm]
	# 		retract_speed			Retraction speed [mm/s]
	# 		retract_extra_restart	Retraction extra restart distance [mm]
	# 		retract_lift			Retraction lift [mm]
	# 		travel_speed			Travel speed [mm/s]		
	# 		layer0_speed			First  layer print speed [mm/s] 
	# 		fast_speed				Speed on fast part of calibration [mm/s]
	# 		slow_speed				Speed on slow part of calibration [mm/s]
	# 		layer_height			Print layer height [mm]
	# 		layer0_height			First layer height [mm]
	# 		pa_min					Start value for pressure advance alibration [s]
	# 		pa_max					End value for pressure advance alibration [s]
	def __init__(self, name, delta, radius, size_x, size_y, size_z, nozzle, retract_distance, retract_speed, retract_extra_restart, retract_lift, travel_speed, layer0_speed, fast_speed, slow_speed, layer_height, layer0_height, pa_min, pa_max):
		self.name = name
		self.delta = delta
		self.radius = radius
		self.size_x = size_x
		self.size_y = size_y
		self.size_z = size_z
		self.nozzle = nozzle
		self.retract_distance = retract_distance
		self.retract_speed = retract_speed
		self.retract_extra_restart = retract_extra_restart
		self.retract_lift = retract_lift
		self.travel_speed = travel_speed
		self.layer0_speed = layer0_speed
		self.fast_speed = fast_speed
		self.slow_speed = slow_speed
		self.layer_height = layer_height
		self.layer0_height = layer0_height
		self.pa_min = pa_min
		self.pa_max = pa_max

		if delta:
			self.center_x = 0
			self.center_y = 0
		else:
			self.center_x = size_x/2
			self.center_y = size_y/2

# GCode class, helper to generate G-code
class GCode:
	# GCode constructor
	def __init__(self, filename, printer, filament):
		self.curr_x = 0
		self.curr_y = 0
		self.curr_z = 0
		self.curr_e = 0
		self.curr_f = 0
		self.filament_area = pi*(filament.diameter/2)**2
		self.extrusion_factor = filament.extrusion_factor
		self.filament_density = filament.density
		self.extrusion_width = printer.nozzle*1.125
		self.retract_distance = printer.retract_distance
		self.retract_feed = printer.retract_speed*60
		self.retract_extra_restart = printer.retract_extra_restart
		self.retract_lift = printer.retract_lift
		self.retract_lift_speed = printer.travel_speed
		self.file = open(filename, 'w')

	def finish(self):
		self.file.close()		
	
	# Print method, placeholder for future support of generating multiple files
	#	Params:
	#		line	String to print on separate line
	def print(self, line):
		self.file.write(line + "\n")
	
	# Generate move without extrusion
	#	Params:
	#		x		target x position [mm]
	#		y		target y position [mm]
	#		z		target z position [mm]
	#		speed	movement speed [mm/s]
	def move(self, x, y, z, speed):
		cmd = "G1"
		
		# Position
		if x != self.curr_x:
			cmd += " X%.3f" % x
			self.curr_x = x
		if y != self.curr_y:
			cmd += " Y%.3f" % y
			self.curr_y = y
		if z != self.curr_z:
			cmd += " Z%.3f" % z
			self.curr_z = z
			
		# Feed
		feed = speed * 60
		if feed != self.curr_f:
			cmd += " F%d" % feed
			self.curr_f = feed
		
		if cmd != "G1":
			self.print(cmd)

	# Generate relative move without extrusion
	#	Param:
	#		x		relative x distance [mm]
	#		y		relative y distance [mm]
	#		z		relative z distance [mm]
	#		speed	movement speed [mm/s]
	def rel_move(self, x, y, z, speed):
		self.move(self.curr_x + x, self.curr_y + y, self.curr_z + z, speed)
	
	# Generate extrude command
	#	Params:
	#		x		target x position [mm]
	#		y		target y position [mm]
	#		z		target z position [mm]
	#		speed	movement speed [mm/s]
	#		height	Print height [mm]
	def extrude(self, x, y, z, speed, height):
		# calculations from http://manual.slic3r.org/advanced/flow-math
		area = (self.extrusion_width-height)*height+(height/2)**2*pi
		length = sqrt((x-self.curr_x)**2 + (y-self.curr_y)**2 + (z-self.curr_z)**2)
		volume = length * area * self.extrusion_factor
		
		cmd = "G1"		

		# Position
		if x != self.curr_x:
			cmd +=	" X%.3f" % x
			self.curr_x = x
		if y != self.curr_y:
			cmd += " Y%.3f" % y
			self.curr_y = y
		if z != self.curr_z:
			cmd += " Z%.3f" % z
			self.curr_z = z

		# Extrusion
		if volume > 0:
			self.curr_e += volume/self.filament_area
			cmd += " E%.3f" % self.curr_e
		
		# Feed
		feed = speed * 60
		if feed != self.curr_f:
			cmd += " F%d" % feed
			self.curr_f = feed

		self.print(cmd)
	
	# Generate retract
	def retract(self):
		self.curr_e -= self.retract_distance
		self.print("G1 E%.3f F%d" % (self.curr_e, self.retract_feed))
		self.move(self.curr_x, self.curr_y, self.curr_z+self.retract_lift, self.retract_lift_speed)
	
	# Genreate de-retract
	def deretract(self):
		self.move(self.curr_x, self.curr_y, self.curr_z-self.retract_lift, self.retract_lift_speed)
		self.curr_e += self.retract_distance + self.retract_extra_restart
		self.print("G1 E%.3f F%d" % (self.curr_e, self.retract_feed))
	
	# Set bed temperature
	#	Params:
	#		temp	Bed temperature [deg C]
	def set_bed_temp(self, temp):
		self.print("M140 S%d" % temp)
	
	# Set bed temperature and wait for it to be reached
	#	Params:
	#		temp	Bed temperature [deg C]
	def set_bed_temp_wait(self, temp):
		self.print("M190 S%d" % temp)
		
	# Set hotend temperature
	#	Params:
	#		temp	Hotend temperature [deg C]
	def set_hotend_temp(self, temp):
		self.print("M104 S%d" % temp)

	# Set hotend temperature and wait for it to be reached
	#	Params:
	#		temp	Hotend temperature [deg C]
	def set_hotend_temp_wait(self, temp):
		self.print("M109 S%d" % temp)
	
	# Set fan speed
	#	Params:
	#		speed	Fan speed [%]
	def set_fan_speed(self, speed):
		pwm = speed/100
		if pwm < 0:
			pwm = 0
		elif pwm > 1:
			pwm = 1
		self.print("M106 S%.2f" % pwm)
	
	# Set pressure advance
	# 	Params:
	#		pressure_advance	Pressure advance factor [mm*s*s]
	def set_pressure_advance(self, pressure_advance):
		self.print("M572 D0 S%.3f" % pressure_advance)
	
	# Misc. init commands
	def init(self):
		self.print("G21")
		self.print("M82")
		self.print("G92 E0")
		self.print("G90")
	
	# Home one or more axis
	#	Params:
	#		x 	Home X-axis [bool]
	#		y 	Home Y-axis [bool]
	#		z 	Home Z-axis [bool]
	def home(self, x, y, z):
		cmd = "G28"
		if not x or not y or not z:
			if x:
				cmd += " X"
			if y:
				cmd += " Y"
			if z:
				cmd += " Z"
		self.print(cmd)
	
	# Use absolute prositions
	def absolute_pos(self):
		self.print("G90")
		
	# Use relative positions
	def relative_pos(self):
		self.print("G91")
	
	# Disable motor drivers
	def disable_motors(self):
		self.print("M18")
	
	# Generate comment in g-code
	# 	Params:
	#		comment		Comment string to  put in G-code
	def comment(self, comment):
		self.print("; " + comment)

# Class for generating calibration cylinders
class CalibCylinder:
	# Constructor for CalibCylinder
	#	Params:
	#		radius		Cylinder radius
	#		segments	Number of straight line segments to split cylinder into
	#		layers		Number of layers to print
	#		brims		Number of brims to print on first layer
	def __init__(self, radius, segments, layers, brims):
		self.r = radius
		self.segments = segments
		self.layers = layers
		self.brims = brims
	
	# Helper function to generate a range of angles given a number of circle segments
	def angles(self):
		a = 0
		while a < 2*pi:
			yield a
			a += 2*pi/self.segments
	
	# Function to generate gcode for a calibration cylinder
	#	Params:
	#		filename	The file to write to
	#		printer		Printer class to generate for
	#		filament	Filament to generate for
	def generate(self, filename, printer, filament):
		gcode = GCode(filename, printer, filament)

		x = printer.center_x
		y = printer.center_y

		# Prefix
		gcode.comment("Pressure advance calibration cylinder for RepRapFirmware")
		gcode.comment("generated by LHelge pa_cal_v2.py on %s" % datetime.datetime.now() )
		gcode.comment("")
		gcode.comment("For printer: %s (%.2f mm nozzle)" % (printer.name, printer.nozzle))
		gcode.comment("With filament: %s (%.2f)" % (filament.name, filament.diameter))
		gcode.comment("  First layer:      height=%.2f mm, bed temp=%d C, print temp=%d C, fan speed=%d%%" % (printer.layer0_height, filament.bed_layer0_temp, filament.hotend_layer0_temp, filament.fan_layer0_speed))
		gcode.comment("  Following layers: height=%.2f mm, bed temp=%d C, print temp=%d C, fan speed=%d%%" % (printer.layer_height, filament.bed_temp, filament.hotend_temp, filament.fan_speed))
		gcode.comment("")
		gcode.comment("Cylindrical object (r=%.1f mm, %d layers)" % (self.r, self.layers))
		gcode.comment("  Layer 0 PA: %.3f" % printer.pa_min)
		gcode.comment("  Layer %d PA: %.3f" % (self.layers, printer.pa_max))

		# init
		gcode.set_bed_temp_wait(filament.bed_layer0_temp)
		gcode.set_hotend_temp(filament.hotend_layer0_temp)
		gcode.init()
		gcode.home(True, True, True)
		gcode.move(x + self.r + self.brims*gcode.extrusion_width, y, 5, printer.travel_speed)
		gcode.set_hotend_temp_wait(filament.hotend_layer0_temp)
		gcode.set_fan_speed(filament.fan_layer0_speed)
		
		#brim
		for b in range(self.brims, 0, -1):
			r = self.r + b*gcode.extrusion_width
			gcode.comment("Brim %d, r=%.3f" % (b, r))
			gcode.move(x + r, y, printer.layer0_height, printer.travel_speed)
			for a in self.angles():
				gcode.extrude(x + r*cos(a), y + r*sin(a), printer.layer0_height, printer.layer0_speed, printer.layer0_height)
		
		#adhesion layer
		gcode.comment("Adhesion layer")
		for a in self.angles():
			gcode.extrude(x + self.r*cos(a), y + self.r*sin(a), printer.layer0_height, printer.layer0_speed, printer.layer0_height)

		gcode.set_bed_temp(filament.bed_temp)
		gcode.set_hotend_temp(filament.hotend_temp)
		gcode.set_fan_speed(filament.fan_speed)
		
		#Spiral vase start
		gcode.comment("Spiral vase start")
		for a in self.angles():
			height = printer.layer_height * a/(2*pi)
			gcode.extrude(x + self.r*cos(a), y + self.r*sin(a), printer.layer0_height + height, printer.fast_speed, height)
			
		# Main layers
		gcode.comment("Main layers")
		for l in range(1, self.layers):
			z = printer.layer0_height + l*printer.layer_height
			pa = printer.pa_min + (printer.pa_max - printer.pa_min)*(l/self.layers)
			gcode.comment("Layer %d, Z=%.3f mm, PA=%.3f" % (l, z, pa))
			gcode.set_pressure_advance(pa)
			for a in self.angles():
				speed = printer.fast_speed
				if 0 < a < pi/4 or pi < a < 5*pi/4:
					speed = printer.slow_speed
				gcode.extrude(x + self.r*cos(a), y + self.r*sin(a), z + printer.layer_height*a/(2*pi), speed, printer.layer_height)
				
		# Indicator layer
		gcode.comment("Indicator layers")
		gcode.set_pressure_advance((printer.pa_min+printer.pa_max)/2)
		for l in range(0,2):
			z = printer.layer0_height + (self.layers+l)*printer.layer_height
			printing = True
			for a in self.angles():
				if 0 <= a < pi/4 or pi <= a < 5*pi/4:
					if printing:
						gcode.retract()
						printing = False
				else:
					if not printing:
						gcode.move(x + self.r*cos(a), y + self.r*sin(a), z + printer.layer_height*a/(2*pi) + printer.retract_lift, printer.travel_speed)
						gcode.deretract()
						printing = True
				
				if printing:
					gcode.extrude(x + self.r*cos(a), y + self.r*sin(a), z + printer.layer_height*a/(2*pi), printer.fast_speed, printer.layer_height)
		
		# suffix
		gcode.retract()
		gcode.rel_move(0, 0, 5, printer.travel_speed)
		gcode.home(True, False, False)
		gcode.set_bed_temp(0)
		gcode.set_hotend_temp(0)
		gcode.set_fan_speed(0)
		gcode.disable_motors()

		gcode.comment("filament used = %.1f mm (%.1f cm3, %.1f g)" % (gcode.curr_e, gcode.curr_e*gcode.filament_area/1000, filament.density*gcode.curr_e*gcode.filament_area/1000))

# Filament list
filament_list = []
# (Name, Diameter, Extrusion factor, Density, Bed temp, Layer0 bed temp, Hotend temp, Layer0 hotend temp, Fan speed, Layer0 fan speed)
filament_list.append(Filament("PLA", 1.75, 100, 1.27, 60, 70, 205, 215, 100, 0))
filament_list.append(Filament("PETG", 1.75, 97, 1.27, 90, 70, 260, 245, 50, 0))

# Printer list
printer_list = []
# (Name, Delta, Size X, Size Y, Nozzle, Retract distance, retract speed, Extra restart, Retract lift, Travel speed, Layer0 speed, Fast speed, Slow speed, Layer height, Layer0 height, PA min, PA max)
printer_list.append(Printer("HEvo", False, 0, 290, 290, 400, 0.8, 1.0, 30, 0.2, 0.2, 200, 25, 70, 15, 0.4, 0.25, 0.0, 0.1))
printer_list.append(Printer("P3Steel", False, 0, 180, 180, 180, 0.4, 0.8, 40, 0.1, 0.2, 150, 25, 70, 15, 0.2, 0.25, 0.0, 0.1))



pa_cal_cylinder = CalibCylinder(25, 128, 50, 5)
for printer in printer_list:
	for filament in filament_list:
		dir = Path(printer.name)
		if not dir.exists():
			dir.mkdir()
		pa_cal_cylinder.generate("%s/pa_cal-%s.gcode" % (printer.name, filament.name), printer, filament)






	


	
		
