#! /usr/bin/python3

from myhdl import *

LOW, HIGH = bool(0), bool(1)


def vga640x480 (clk25MhzPulse, reset, vga_hs,vga_vs, vga_videoon, vga_offscreen, hcounter, vcounter):

	# local data
# total resolution = 800 * 521 (640x480 visible) @ 25 Mhz = 60 Hz
	hcounter_tmp = Signal(intbv(0,min=0, max=800))
	vcounter_tmp = Signal(intbv(0,min=0, max=521))
	


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
	#@always(hcounter_tmp.posedge,vcounter_tmp.posedge)
	@always_comb
	def assign():

		nonlocal hcounter_tmp
		nonlocal vcounter_tmp

		if (hcounter_tmp < 96):
			vga_hs.next = 1
			print("1")
		else:
			vga_hs.next = 0
			print("0")

		if (vcounter_tmp < 2):
			vga_vs.next = 1
		else:
			vga_vs.next = 0

		if ((hcounter_tmp >= 144) and (hcounter_tmp < 784) and (vcounter_tmp >= 31) and (vcounter_tmp < 510)):
			vga_videoon.next = 1
		else:
			vga_videoon.next = 0

		# copy counters to output
		if (hcounter_tmp >= 144):
			hcounter.next = hcounter_tmp-144
		else:
			hcounter.next = 0

		if (vcounter_tmp >= 144):
			vcounter.next = vcounter_tmp-144
		else:
			vcounter.next = 0


	# clock driven logic
	@always(clk25MhzPulse.posedge, reset.posedge)
	def Clock25Mhz():

		nonlocal hcounter_tmp
		nonlocal vcounter_tmp

#		print("hcounter = "+str(hcounter_tmp))
#		print("vcounter = "+str(vcounter_tmp))

		if reset == 1:
			hcounter_tmp = 0
			vcounter_tmp = 0
		else:
			if hcounter_tmp != 799:
				hcounter_tmp = hcounter_tmp + 1
			else:
				# end of horizontal line
				hcounter_tmp = 0

				if vcounter_tmp != 520:
					vcounter_tmp = vcounter_tmp + 1
				else:
					vcounter_tmp = 0
			# end horizontal and vertical counters	
		# end else (not reset)
	

	return Clock25Mhz,assign

	

""" 
	test suite
"""

def test_vga640x480():

	# local vars
	clk25MhzPulse, reset, vga_hs,vga_vs, vga_videoon, vga_offscreen = [Signal(bool(0)) for i in range(6)]
	hcounter = Signal(intbv(0,min=0, max=800))
	vcounter = Signal(intbv(0,min=0, max=521))


	vga640x480_inst= vga640x480 (clk25MhzPulse, reset, vga_hs,vga_vs, vga_videoon, vga_offscreen, hcounter, vcounter)

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

