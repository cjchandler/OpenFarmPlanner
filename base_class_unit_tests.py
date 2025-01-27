#base class unit tests: 
#this is to make sure all the classes init and save to json correctly, or at least without crashing 

from crop_event import * 
CE = demo5_crop_event()
CE.dump_to_json( "./event1.json")
CE.load_from_json( "event1.json")
CE.pretty_print()

from cultivar import * 
saladbowl = cultivar()
saladbowl.dump_to_json( "./" )
saladbowl.load_from_json("./saladbowl_cultivar.json")
print( saladbowl.details)
