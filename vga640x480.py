#! /usr/bin/python3

from myhdl import *

LOW, HIGH = bool(0), bool(1)


def vga640x480 (clk25MhzPulse, reset, vga_hs,vga_vs, vga_videoon, vga_offscreen, hcounter_external, vcounter_external):

	# local data
	# total resolution = 800 * 521 (640x480 visible) @ 25 Mhz = 60 Hz
	hcounter_internal = Signal(intbv(0,min=0, max=800)[10:])
	vcounter_internal = Signal(intbv(0,min=0, max=521)[10:])
	


	""" vga640x480 generator
	input:	25Mhz clock
				reset
	output:	vga_hs (horizontal sync)
				vga_vs (vertical sync)
				vga_videoon (video on, visible screen)
				vga_offscreen (vga is above or below visible screen)
				hcounter: horizontal counter: 0 to 799
				vcounter: vertical counter: 0 to 599
	"""


	# combinatory logic
	@always_comb
	def assign():

		if (hcounter_internal < 96):
			vga_hs.next = 1
# DEBUG
			print("1")
		else:
			vga_hs.next = 0
# DEBUG
			print("0")

		if (vcounter_internal < 2):
			vga_vs.next = 1
		else:
			vga_vs.next = 0

		if ((hcounter_internal >= 144) and (hcounter_internal < 784) and (vcounter_internal >= 31) and (vcounter_internal < 510)):
			vga_videoon.next = 1
		else:
			vga_videoon.next = 0

		# copy counters to output
		if (hcounter_internal >= 144):
			hcounter_external.next = hcounter_internal-144
		else:
			hcounter_external.next = 0

		if (vcounter_internal >= 144):
			vcounter_external.next = vcounter_internal-144
		else:
			vcounter_external.next = 0


	# clock driven logic
	@always(clk25MhzPulse.posedge, reset.posedge)
	def Clock25Mhz():

		nonlocal hcounter_internal
		nonlocal vcounter_internal

# DEBUG
#		print("hcounter = "+str(hcounter_internal))
#		print("vcounter = "+str(vcounter_internal))

		if reset == 1:
			hcounter_internal = 0
			vcounter_internal = 0
		else:
			if hcounter_internal != 799:
				hcounter_internal += 1
			else:
				# end of horizontal line
				hcounter_internal = 0

				if vcounter_internal != 520:
					vcounter_internal += 1
				else:
					vcounter_internal = 0
			# end horizontal and vertical counters	
		# end else (not reset)
	

	return Clock25Mhz,assign

	

""" 
	test suite
"""

def test_vga640x480():

	# local vars
	clk25MhzPulse, reset, vga_hs,vga_vs, vga_videoon, vga_offscreen = [Signal(bool(0)) for i in range(6)]
	hcounter_external = Signal(intbv(0,min=0, max=800)[10:])
	vcounter_external = Signal(intbv(0,min=0, max=521)[10:])


	vga640x480_inst= vga640x480 (clk25MhzPulse, reset, vga_hs,vga_vs, vga_videoon, vga_offscreen, hcounter_external, vcounter_external)

	@always(delay(10))
	def clkgen():
		clk25MhzPulse.next = not clk25MhzPulse

	@instance
	def stimulus():
		reset.next = HIGH
		yield delay(100)
		reset.next = LOW


	return vga640x480_inst, clkgen, stimulus

"""
	simulation
"""


def simulate(timesteps):
	tb = traceSignals(test_vga640x480)
	sim = Simulation(tb)
	sim.run(timesteps)

simulate(2000000)


