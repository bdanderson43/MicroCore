from opentrons import protocol_api

# tweakable settings

# metadata 
metadata = {
	'protocolName': 'Strain Collection 384 Well Growth Curve Setup', 
	'author': 'J Bisanz and B Anderson, bda5161@psu.edu',
	'description': 'Transfer strains from 96 well growth plate to 2x 384 plates with test compound pre-loaded. Tips returned to box to be discarded!',
	'apiLevel': '2.20'
}

def add_parameters(parameters: protocol_api.Parameters):

	parameters.add_bool(
    	variable_name="regenerate_plate",
    	display_name="Regenerate Source Plate?",
    	description="Make source plate for future run",
    	default=False
)

	parameters.add_int(
    	variable_name="mix_number",
    	display_name="Times to mix source plate",
    	description="Number of Mix cycles, twice is enough",
    	default= 2,
    	choices=[
    	{"display_name" : "Once", "value" : 1},
    	{"display_name" : "Twice", "value" : 2},
    	{"display_name" : "Three times", "value" : 3}]
)

def run(protocol: protocol_api.ProtocolContext):

	# define labware and locations on the deck
	# tips 
	tips = protocol.load_labware('opentrons_96_filtertiprack_20ul', '6', 'p20_Tips') # 20ul filter tips on deck position 6 
	
	# Source plate containing 150 uL liquid cultures of each strain
	cultureplate = protocol.load_labware('corning_96_wellplate_360ul_flat', '3', 'Source_Plate')

	# 2 identical 384 plate pre-loaded with media and test compound to be used in growth curves 
	assayplate1 = protocol.load_labware('corning_384_wellplate_112ul_flat', '1', '384_Plate_1')
	assayplate2 = protocol.load_labware('corning_384_wellplate_112ul_flat', '2', '384_Plate_2')
	
	# New Source Plate to regenerate cultures if needed, should have 150 uL of fresh media
	regenerate_culture_volume = 0
	
	if protocol.params.regenerate_plate is True: 
		cultureplate2 = protocol.load_labware('corning_96_wellplate_360ul_flat', '4', 'New_Source_Plate')
		# volume to add to strain to regenerate culture only if regenerating (in uL)
		# volume to add to strain to regenerate culture only if regenerating (in uL)

		regenerate_culture_volume = 1.5	
	# define pipettes 
	multi20 = protocol.load_instrument('p20_multi_gen2', 'right', tip_racks=[tips])
	
	# decrease pipette speed to reduce risk of cross-contamination. 
	multi20.default_speed = 100
	
	culture_volume = 0.8 
	
	
	# volume to aspirate from each well which is 10% more than the volume to dispense to avoid air bubbles
	aspirate_volume = (culture_volume*8 + regenerate_culture_volume) * 1.1

# transfer cultures from the source plate to the 384 well plates first the vehicle control wells then the drug wells. Also transfer to new source plate if regenerating. 
# The range of 1-13 is used to loop through all the columns of the 96 well plate and transfer to the corresponding wells in the 384 well plates.
	for i in range(1, 13):
		multi20.pick_up_tip()
		
		for j in range(1,protocol.params.mix_number):
			# mix culture before taking out of well to disrupt any cell pellets
			multi20.mix(2, 20,cultureplate['A'+str(i)]) 
			
			# Mix at top of well to avoid bubbles and to more effectively mix culture
			multi20.mix(2, 20,cultureplate['A'+str(i)].bottom(z=3))  
			
			# final mix at normal height to ensure no cells are left behind
			multi20.mix(2, 20,cultureplate['A'+str(i)]) 
		
		# aspirate culture from source plate	
		multi20.aspirate(Culture_Volume*9, cultureplate['A'+str(i)]) # pull one extra load dead volume

		# add to new source plate if regenerating 
		if protocol.params.regenerate_plate is True:
			multi20.dispense(regenerate_culture_volume, cultureplate2['A'+str(i)])

		# add culture to vehicle control wells of 384 well plates
		multi20.dispense(Culture_Volume, assayplate1['A'+str(i*2-1)])
		multi20.dispense(Culture_Volume, assayplate1['A'+str(i*2)])
		multi20.dispense(Culture_Volume, assayplate2['A'+str(i*2-1)])
		multi20.dispense(Culture_Volume, assayplate2['A'+str(i*2)])

		# add culture to vehicle drug wells of 384 well plates
		multi20.dispense(Culture_Volume, assayplate2['B'+str(i*2)])
		multi20.dispense(Culture_Volume, assayplate2['B'+str(i*2-1)])
		multi20.dispense(Culture_Volume, assayplate1['B'+str(i*2)])
		multi20.dispense(Culture_Volume, assayplate1['B'+str(i*2-1)])
		
		# return tip to tip box to be discarded
		multi20.return_tip()
	
	# end of protocol
	protocol.comment('Protocol complete!')
