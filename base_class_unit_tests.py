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

from soil_plot import *
s = soil_plot()
s.details['id'] = "testid"
s.dump_to_json("./")
ss = soil_plot()
ss.load_from_json("./testid_soil_plot.json")
assert( ss.details['id'] == "testid")


from crop_plan import * 

lettuce_plan = crop_plan()
lettuce_plan.soil_plots.append(s)
lettuce_plan.event_list.append( demo1_crop_event() )
lettuce_plan.event_list.append( demo2_crop_event() )
lettuce_plan.event_list.append( demo3_crop_event() )
lettuce_plan.event_list.append( demo4_crop_event() )
lettuce_plan.event_list.append( demo5_crop_event() )
lettuce_plan.print_plan()

dirdump=lettuce_plan.dump_to_json("./")
lettuce_plan2 = crop_plan()
lettuce_plan2.cultivar.details['name'] = "redwood"
lettuce_plan2.load_crop_plan_from_dir(dirdump)
lettuce_plan2.print_plan()

assert( lettuce_plan2.cultivar.details['name']=="saladbowl")
assert( lettuce_plan2.soil_plots[0].details['id']=="testid")

from weather import *
W = weather()
dt = datetime(2024,3,25)
W.last_observed_time = dt.timestamp() 
W.load_observed_weather()
W.fill_with_prediction(365, True)
