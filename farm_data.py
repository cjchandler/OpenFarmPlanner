import geopy
import geopy.distance
import numpy as np
import pandas as pd
import time
import datetime




def date_string_to_timestamp( datestring):
    l = datestring.split('-')
    dt= datetime.datetime(int(l[2]), int(l[1]) , int(l[0]) )
    timestamp = (dt - datetime(1970, 1, 1)) / timedelta(seconds=1)
    return timestamp

def timestamp_to_date( ts):
    dt_object = datetime.fromtimestamp(timestamp)
    return str(dt_object.day) + '-' + str(dt_object.month) + '-' + str(dt_object.year)

# farm planner farm class 
class farm_data:
    def __init__(self):
        self.farm_address = "South Ohio, NS"
        self.farm_name = "TestFarm" 
        self.soil_plot_list = []
        self.active_crop_plan_list = []
        #archive data? 
            #we will need a way to get this all together from file when we need it 
            
        #economic information, what are the seaonal demand curves looking like for each crop?
    

class weather:
    def __init__(self):
        self.last_observed_time = 0 #this is timestamp for the last actual data we have, after that it's all prediction
        self.df_daily = pd.DataFrame() #this is observed and forcast weather all in a lump so we can run the crop model 
        self.df_observed = pd.DataFrame() #real weather as observed
        #weather df format:[ 'Day', 'Month' , 'Year' , 'Tmin(C)' , 'Tmax(C)' , 'Prcp(mm)' , 'ET0']
        
    def load_observed_weather(self):
        self.df_observed = pd.read_csv() 
        
    def fill_with_prediction_to( self, end_date_str):
        #look at the observed weather and guess at the future weather
        

class soil_plot:
    def __init__(self):
        self.details  = {}
        self.details['id'] = time.time() #unique identifier. pick something better later I guess
        self.details['soil_type'] = "clay loam" 
        self.details['water_saturation_fraction'] = 1.0 
        self.details['water_field_capacity_mm/m2'] = 60
        self.details['area_m2'] = 1.0
        self.details['corner_gps_points'] = [ "0,0" , "0,0" , "0,0" , "0,0"] 
        self.details['current_cultivar'] = "NONE"
        self.details['current_crop_biomass_kg'] = 0
        self.details['canopy_coverage_fraction'] =0 
           

class crop_plan:
    def __init__(self):
        self.event_list = [] 
        self.details = {}
        self.details['cultivar'] = " " 
        self.details[''] = " " 
    
         
    def make_all_events(self):
        #well obviosly there needs to be a data base of how to do each crop. 
        #then we also can look back at other times we did this crop
        
        print("This is setting up the crop plan. What is the cultivar name?")
        n = input()
        self.details['cultivar'] = lower(n) 

        #TODO look in the archives, have we done this before? 
        previous_same_crops = False 
        # ~ if(previous_same_crops == False):
            #add some basic events:
            #soil prep 
            
            #planting 
            #weeding
            #harvesting 

    def set_event_times(self , planting_date ):
        for e in self.event_list:
            if e.details['days after planting'] == 0 or e.details['growing degree days after planting'] == 0
                #this is the planting date. 
                e.computer_details['planned_timestamp'] = date_string_to_timestamp(planting_date)
            #if there are any fixed times, we can do those too: 
            elif e.details['days after planting'] != 999999 and e.details['days after planting'] != '':
                e.computer_details['planned_timestamp'] = date_string_to_timestamp(planting_date) + e.details['days after planting']*60*60*24
                
        #ok, now we we need to load real + projected weather so we can fill in the times for the gdd dependent events


        
class crop_event:
    def __init__(self):
        self.details = {}
        self.details['event_name'] = "name of event"
        self.details['human_instructions'] = " walk to farm "
        self.details['time_estimate_min'] = 0
        self.details['time_taken_min'] = -1
        self.details['soil_plot_ids'] =  []
        self.details['tools used'] = ["boots", "coat"]
        self.details['consumables_used'] = ["string"]
        self.details['days after planting'] = 999999
        self.details['growing degree days after planting'] = 999999
        
        self.computer_details = {} #this is stuff that the farmer should never have to adjust manually in .csv 
        self.computer_details['planned_timestamp'] = ' ' 
        self.computer_details['actual_timestamp_start'] = ' ' 
        self.computer_details['actual_timestamp_end'] = ' ' 
 
      
    def load_from_csv(self , filename ):
        df = pd.read_csv(filename) 
        keys = df.columns.to_list()
        D = df.to_numpy()
        print(keys)
        print(D)
        
        for i, val in enumerate(keys):
            col_values = D[:,i]
            l = [x for x in col_values if str(x) != 'nan']
            # ~ print(l)
            self.details[val] = l
        
        print(self.details)
       

        
    def save_as_csv(self , filename ):
        max_len = 0
        for k in self.details:
            print(self.details[k])
            if isinstance(self.details[k], list):
                
                if( len( self.details[k]) > max_len):
                    max_len = len( self.details[k])
        print("max_len" , max_len  ) 
        for k in self.details:
            if  isinstance(self.details[k], list) == True:
                #add padding with 0 or " "
                n_padding = max_len - len(self.details[k]) 
                self.details[k] = self.details[k]+ [""]*n_padding 
            if  isinstance(self.details[k], list) == False:
                start_list = [ self.details[k] ]
                n_padding = max_len - 1 
                self.details[k] = start_list + [""]*n_padding 
            
        df = pd.DataFrame(self.details)
        df.to_csv(filename)



CE = crop_event()
CE.save_as_csv("my_test_event.csv")
CE.load_from_csv("plant_lettuce_event.csv")
 

# Define starting point.
start = geopy.Point(42.91298, -66.071038)

# Define a general distance object, initialized with a distance of 1 m.
d = geopy.distance.distance(kilometers = 0.001)

# Use the `destination` method with a bearing of 0 degrees (which is north)
# in order to go from point `start` 1 m to north.
pN =   d.destination(point=start, bearing=0)
pNE =   d.destination(point=pN, bearing=90)
pNES =   d.destination(point=pNE, bearing=180)

s1 = soil_plot()
s1.details['corner_gps_points'] = [ start , pN , pNE , pNES ] 

CE.details["soil_plot_list"] = [s1.details["id"] ]

lettuce_plan = crop_plan()
lettuce_plan.details['cultivar'] = 'salad bowl' 

soil_prep = crop_event()
soil_prep.load_from_csv( "./lettuce_event_templates/prepare_soil_tarps_event.csv")

planting = crop_event()
planting.load_from_csv( "./lettuce_event_templates/plant_lettuce_event.csv")

weeding = crop_event()
weeding.load_from_csv( "./lettuce_event_templates/weed_lettuce_event.csv")

harvesting = crop_event()
harvesting.load_from_csv( "./lettuce_event_templates/harvest_lettuce_event.csv")

post_harvesting = crop_event()
post_harvesting.load_from_csv( "./lettuce_event_templates/post_harvest_lettuce_event.csv")

lettuce_plan.event_list = [ soil_prep , planting , harvesting , post_harvesting] 
#so these are all the events, but they don't have any times associated with them 

