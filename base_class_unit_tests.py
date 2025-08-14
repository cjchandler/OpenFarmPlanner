#base class unit tests: 
#this is to make sure all the classes init and save to json correctly, or at least without crashing 

from crop_event import * 
CE = demo5_crop_event()
CE.dump_to_json( "./unit_test_dump/event1.json")
CE.load_from_json( "./unit_test_dump/event1.json")
CE.pretty_print()

from cultivar import * 
saladbowl = cultivar()
saladbowl.dump_to_json( "./unit_test_dump/" )
saladbowl.load_from_json("./unit_test_dump/saladbowl_cultivar.json")
print( saladbowl.details)

from soil_plot import *
s = soil_plot()
s.details['id'] = "testid"
s.details['soil_type'] = "bare rock"
s.dump_to_json("./unit_test_dump/")
ss = soil_plot()
ss.load_from_json("./unit_test_dump/testid_soil_plot.json")
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

dirdump=lettuce_plan.dump_to_json("./unit_test_dump/")
lettuce_plan2 = crop_plan()
lettuce_plan2.cultivar.details['name'] = "redwood"
lettuce_plan2.load_crop_plan_from_dir(dirdump)
lettuce_plan2.print_plan()

assert( lettuce_plan2.cultivar.details['name']=="saladbowl")
assert( lettuce_plan2.soil_plots[0].details['id']=="testid")

from weather import *
W = weather()
dt = datetime(2025,1,25)
W.last_observed_time = dt.timestamp() 
W.load_observed_weather()
W.fill_with_prediction(365, True)

from farm_data import *
my_farm = farm_data()
my_farm.details["farm_name"] = "cff"
my_farm.details["farm_address"] = "801hwy340"
my_farm.active_crop_plan_list.append( lettuce_plan2)
my_farm.soil_plot_dict["testid"] = s
my_farm.dump_to_json( "./farm_data_testing/" )

my_loadedfarm = farm_data()
my_loadedfarm.details["farm_name"] = "cff"
my_loadedfarm.load_recent_from_json("./farm_data_testing/")

assert(my_loadedfarm.details["farm_address"] == "801hwy340")
print(my_loadedfarm.soil_plot_dict['testid'].details)
print(s.details['soil_type'])
print( my_loadedfarm.soil_plot_dict['testid'])
assert( my_loadedfarm.soil_plot_dict['testid'].details['soil_type'] == s.details['soil_type'])
assert( my_loadedfarm.soil_plot_dict['testid'].details['water_field_capacity_mm/m2'] == s.details['water_field_capacity_mm/m2'])
assert( my_loadedfarm.active_crop_plan_list[0].cultivar.details['name'] == lettuce_plan2.cultivar.details['name'] )

print("passed loading details")
