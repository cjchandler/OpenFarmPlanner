#crop event 
import geopy
import geopy.distance
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
from aquacrop import aquacrop_wrapper
import pprint
import pickle
import glob
import random
import json





class crop_event:
    def __init__(self):
        self.details = {}
        self.details['event_name'] = "name of event"
        self.details['human_instructions'] = " walk to farm "
        self.details['time_estimate_min_per_m2'] = 0
        self.details['time_estimate_generated'] = 0
        self.details['time_taken_min'] = -1
        self.details['worker_id'] = ''
        self.details['soil_plot_ids'] =  []
        self.details['tools used'] = ["boots", "coat"]
        self.details['consumables_used'] = ["string"]
        self.details['days after planting'] = 'q'
        self.details['growing degree days after planting'] = 'q'
        self.details['is harvest step'] = -1 #-1 or '' is before harvesting. 0 is first harvest step, 1 is next etc  
        
        #  #this is stuff that the farmer should never have to adjust manually in .csv 
        self.details['planned_timestamp'] = 0 
        self.details['actual_timestamp_start'] = -1 
        self.details['actual_timestamp_end'] = -1
        self.details['is_finished'] = False 
 
    def dump_to_json(self ,  pathfilename):
        dtn = datetime.now()
        filename = pathfilename  
        out_file = open(filename, "w")

        json.dump(self.details, out_file, indent = 6)

        out_file.close()
 
    def load_from_json(self , filename):
        with open(filename) as f:
            self.details = json.load(f)
 
    
    def compare_events( self , eB ):

        if self.details['human_instructions'] != eB.details['human_instructions']: 
            return False
        if self.details['worker_id'] != eB.details['worker_id']: 
            return False
        
        return True
    
    def pretty_print(self):
        planneddt = datetime.fromtimestamp(self.details['planned_timestamp'])
        print( "----" + self.details['event_name'] + "----  planned for " + planneddt.strftime('%d-%m-%Y') )
        for i, (key, val) in enumerate(self.details.items()):
            print("    " + key  + "  :   " + str(val) )
            
        
    
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
            if len(l) ==1 :
                self.details[val] = l[0]
        
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
        

def demo1_crop_event():
    de = crop_event()
  
    de.details['event_name'] = "prepare soil"
    de.details['human_instructions'] = "Add compost or other fertilizer to seedbed. lay out black tarps on seedbed. Cover with clear poly. Bury the edges for wind  "
    
    de.details['time_estimate_min_per_m2'] = 5
    de.details['time_estimate_generated'] = 0
    de.details['time_taken_min'] = -1
    de.details['worker_id'] = ''
    de.details['soil_plot_ids'] =  []
    de.details['tools used'] = ["black tarp", "greenhouse plastic" , "shovel"]
    de.details['consumables_used'] = ["compost"]
    de.details['days after planting'] = -10
    de.details['growing degree days after planting'] = 'q'
    de.details['is harvest step'] = -1 #-1 or '' is before harvesting. 0 is first harvest step, 1 is next etc  
    
    de.details['planned_timestamp'] = 0 
    de.details['actual_timestamp_start'] = -1 
    de.details['actual_timestamp_end'] = -1
    de.details['is_finished'] = False 
    return de

def demo2_crop_event():
    de = crop_event()
  
    de.details['event_name'] = "planting"
    de.details['human_instructions'] = "make rows 1 cm deep, 12 inches apart. Seed 3 cm spacing and cover with light dirt. Press down and water"
    de.details['time_estimate_min_per_m2'] = 8
    de.details['time_estimate_generated'] = 0
    de.details['time_taken_min'] = -1
    de.details['worker_id'] = ''
    de.details['soil_plot_ids'] =  []
    de.details['tools used'] = ["hoe", "boots" ]
    de.details['consumables_used'] = ["seed"]
    de.details['days after planting'] = 0
    de.details['growing degree days after planting'] = 0
    de.details['is harvest step'] = -1 #-1 or '' is before harvesting. 0 is first harvest step, 1 is next etc  
    
    de.details['planned_timestamp'] = 2000000
    de.details['actual_timestamp_start'] = -1 
    de.details['actual_timestamp_end'] = -1
    de.details['is_finished'] = False
    return de 

def demo3_crop_event():
    de = crop_event()
  
    de.details['event_name'] = "weeding"
    de.details['human_instructions'] = "hoe between rows"
    de.details['time_estimate_min_per_m2'] = 4
    de.details['time_estimate_generated'] = 0
    de.details['time_taken_min'] = -1
    de.details['worker_id'] = ''
    de.details['soil_plot_ids'] =  []
    de.details['tools used'] = ["hoe", "boots" ]
    de.details['consumables_used'] = []
    de.details['days after planting'] = ""
    de.details['growing degree days after planting'] = 200
    de.details['is harvest step'] = -1 #-1 or '' is before harvesting. 0 is first harvest step, 1 is next etc  
    
    de.details['planned_timestamp'] = 3000000
    de.details['actual_timestamp_start'] = -1 
    de.details['actual_timestamp_end'] = -1
    de.details['is_finished'] = False
    return de 

def demo4_crop_event():
    de = crop_event()
  
    de.details['event_name'] = "harvest"
    de.details['human_instructions'] = "cut head in checker board pattern to leave space for the others to grow bigger. Use a a knife on main root under the leaves"
    de.details['time_estimate_min_per_m2'] = 5
    de.details['time_estimate_generated'] = 0
    de.details['time_taken_min'] = -1
    de.details['worker_id'] = ''
    de.details['soil_plot_ids'] =  []
    de.details['tools used'] = ["knife", "basket" ]
    de.details['consumables_used'] = []
    de.details['days after planting'] = ""
    de.details['growing degree days after planting'] = ""
    de.details['is harvest step'] = 0 #-1 or '' is before harvesting. 0 is first harvest step, 1 is next etc  
    
    de.details['planned_timestamp'] = 4000000
    de.details['actual_timestamp_start'] = -1 
    de.details['actual_timestamp_end'] = -1
    de.details['is_finished'] = False
    return de 
    
def demo5_crop_event():
    de = crop_event()
  
    de.details['event_name'] = "post harvest"
    de.details['human_instructions'] = "put lettuce in water tub with blower for agitation. Remove after 15 min, put on rack to dry for 15 min. Place in plastic bags for sale, add price stickers"
    de.details['time_estimate_min_per_m2'] = 6
    de.details['time_estimate_generated'] = 0
    de.details['time_taken_min'] = -1
    de.details['worker_id'] = ''
    de.details['soil_plot_ids'] =  []
    de.details['tools used'] = ["washing tub with blown air agitator", "drying rack " ]
    de.details['consumables_used'] = ["plastic bags","price stickers"]
    de.details['days after planting'] = ""
    de.details['growing degree days after planting'] = ""
    de.details['is harvest step'] = 1 #-1 or '' is before harvesting. 0 is first harvest step, 1 is next etc  
    
    de.details['planned_timestamp'] = 5000000
    de.details['actual_timestamp_start'] = -1 
    de.details['actual_timestamp_end'] = -1
    de.details['is_finished'] = False
    return de 


