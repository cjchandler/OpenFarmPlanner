import geopy
import geopy.distance
import numpy as np
import pandas as pd


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
    
class soil_plot:
    def __init__(self):
        self.details  = {}
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

        
class crop_event:
    def __init__(self):
        self.details = {}
        self.details['event_name'] = "name of event"
        self.details['human_instructions'] = " walk to farm "
        self.details['time_estimate_min'] = 0
        self.details['time_taken_min'] = -1
        self.details['soil_plot_list'] =  []
        self.details['tools used'] = ["boots", "coat"]
        self.details['consumables_used'] = ["string"]

    # ~ def command_line_event_fill(self):
        # ~ print( "what is the event name?")
        # ~ x = input()
        # ~ self.details['event_name'] = x 
        
        # ~ print( "what are the instructions?")
        # ~ x = input()
        # ~ self.details['human_instructions'] = x 
        
        # ~ print( "what is the time estimate in min?")
        # ~ x = input()
        # ~ self.details['time_estimate_min'] = x 
      
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

CE.details["soil_plot_list"] = [s1]


