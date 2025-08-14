#make a gui testing farm_data class 
import sys
import os

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory by going one level up
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)

# importing
from soil_plot import *


s = soil_plot()
s.details['id'] = "testid"
s.details['soil_type'] = "bare rock"

from crop_plan import * 

lettuce_plan = crop_plan()
lettuce_plan.soil_plots.append(s)
lettuce_plan.event_list.append( demo1_crop_event() )
lettuce_plan.event_list.append( demo2_crop_event() )
lettuce_plan.event_list.append( demo3_crop_event() )
lettuce_plan.event_list.append( demo4_crop_event() )
lettuce_plan.event_list.append( demo5_crop_event() )

#make the dates for today: 
lettuce_plan.event_list[0].details['planned_timestamp'] = time.time() - 24*60*60 
lettuce_plan.event_list[1].details['planned_timestamp'] = time.time()  
lettuce_plan.event_list[3].details['planned_timestamp'] = time.time() + 24*60*60 


from farm_data import *
my_farm = farm_data()
my_farm.details["farm_name"] = "gui_test_farm"
my_farm.details["farm_address"] = "cyberspace"
my_farm.active_crop_plan_list.append( lettuce_plan)
