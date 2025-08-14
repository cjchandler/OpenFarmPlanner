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
import os

from cultivar import *
from crop_event import *
from soil_plot import *

class crop_plan:
    def __init__(self):
        self.event_list = [] 
        self.simdf = pd.DataFrame()
        self.cultivar = cultivar() 
        self.soil_plots = [] #each soil plot has an area, so this is how to figure out how much we are planting
        
        self.details = {}
        self.details['location'] = "placename" #no spaces or special characters here, used as a file name part
        self.details['cropfile.CRO'] = "saladbowl3.CRO" 
        self.details['irrigation.IRR'] = "(NONE)" 
        self.details['minimum_harvest_temperature'] = 0
        self.details['death_temperature'] = 0 #if temeprature goes below this the plant is dead and does not regrow when it gets warmer
    
    
    def dump_to_json(self ,path ):
        ##make a folder, with a unique name
        cultivar = self.cultivar.details['name']
        start_time_stamp = self.event_list[0].details['planned_timestamp']
        start_date_string = datetime.fromtimestamp(start_time_stamp).strftime('%d-%m-%Y ')
        
        dir_name = cultivar + start_date_string 
        dir_name = dir_name.replace(" ", "")
        
        n = 0
        while True: 
            isdir = os.path.isdir(path + dir_name + "_" + str(n) ) #check if this name is taken, is so, up the number until it works
            if isdir == False: 
                dir_name = dir_name + "_" + str(n)
                break
            else:
                n += 1 
                
        os.makedirs(path + dir_name )
        #ok now I can dump all of the things in event list individually, I can dump the cultivar, and I can dump the cropplan details into json files , the simdf as a csv file
        print("saving details")
        self.dump_self_details_to_json(path+dir_name)
        self.cultivar.dump_to_json(path+dir_name)
        self.simdf.to_csv( path+dir_name + "/simdf.csv")
        for i , e in enumerate( self.event_list ):        #then dump all the events in event list... 
            pathfile = path+ dir_name + "/event" + str(i) + ".json"
            e.dump_to_json(pathfile)
        
        for i , s in enumerate( self.soil_plots ):        #then dump all the events in event list... 
            pathfile = path+ dir_name + "/"
            s.dump_to_json(pathfile)
        
        
        return path + dir_name
        
        
 
    def dump_self_details_to_json(self ,path ):
        #look in path, is there an 
        filename = "crop_plan_details.json"
        out_file = open(path+"/"+filename, "w")

        json.dump(self.details, out_file, indent = 6)

        out_file.close()
        
 
    def load_self_details_from_json(self , path_to_crop_plan_dir):
        path = path_to_crop_plan_dir
        
        ##get the details, that's easy 
        with open(path+"/crop_plan_details.json" ) as f:
            self.details = json.load(f)
    
    def load_crop_plan_from_dir(self , path_to_crop_plan_dir):
        path = path_to_crop_plan_dir
        self.load_self_details_from_json(path)
        
        outtest= ""
        
        ##now get the sim .csv
        csvfiles = []
        for filename in glob.glob(path + "/*simdf.csv"):
            csvfiles.append(filename)
        if (     len(csvfiles) == 1 ):
            self.simdf = pd.read_csv( csvfiles[0])
            outtest = outtest+"sim" 
        
        ##now get the cultivar class
        cultivarfiles = []
        for filename in glob.glob(path + "/*cultivar.json"):
            cultivarfiles.append(filename)
        if (     len(cultivarfiles) == 1 ):
            self.cultivar.load_from_json( cultivarfiles[0] )
        
        
        ##now get the events
        eventfiles = []
        for filename in glob.glob(path + "/event*.json"):
            eventfiles.append(filename)
        for ce in eventfiles:
            tempevent = crop_event()
            tempevent.load_from_json( ce)
            self.event_list.append( tempevent)
        
        #the events are out of order, sort them
        self.event_list = sorted( self.event_list, key=lambda x: x.details["planned_timestamp"]) 
        
        #get soil plots 
        ##now get the events
        soilfiles = []
        for filename in glob.glob(path + "/*soil_plot.json"):
            soilfiles.append(filename)
        for sp in soilfiles:
            sptemp = soil_plot()
            sptemp.load_from_json( sp)
            self.soil_plots.append( sptemp)
    
        return outtest
    
        
         
    def make_all_events(self):
        #well obviosly there needs to be a data base of how to do each crop. 
        #then we also can look back at other times we did this crop
        #this is a GUI thing eventually 
        
        print("This is setting up the crop plan. What is the cultivar name?")
        n = input()
        self.details['cultivar'] = lower(n) 

        

    def set_event_times(self , planting_datetime , df_predict):
    
        
        self.simdf = aquacrop_wrapper.simAquaCrop(  self.details['location'], "./aquacrop" , planting_datetime , df_predict['datetime'].iloc[-2] ,  df_predict , self.details['minimum_harvest_temperature'] , self.details['cropfile.CRO'] , self.details['irrigation.IRR']) 
         # ~ = pd.read_csv( "./aquacrop/PRMdayout.csv" ) 
        
        for e in self.event_list:
            realdays = -999 
            realtiming = False
            gddays = -999 
            gddtiming = False
            try: 
                realdays = float(e.details['days after planting'])
                realtiming = True
            except:
                realtiming = False
            
            try: 
                gddays = float(e.details['growing degree days after planting'])
                gddtiming = True
            except:
                gddtiming = False
            
           
                
            # ~ print(e.details['days after planting'] , e.details['growing degree days after planting'])
            # ~ print(realtiming , str(e.details['days after planting']).isdigit(), gddtiming)
            
            ##Make sue this above thing about timing is working right first. 
            
            # ~ #planting event? 
            # ~ if realtiming == True or gddtiming == True: 
                # ~ if float(str(e.details['days after planting'])) == 0 or e.details['growing degree days after planting'] == 0:
                    # ~ #this is the planting date. 
                    # ~ e.computer_details['planned_timestamp'] = datetime.timestamp(planting_datetime)
                     # ~ #don't worry about any other time for this event, you're done
                 
            
            #if it a fixed time? 
            if realtiming == True :
                print('fixed time')
                e.details['planned_timestamp'] = datetime.timestamp(planting_datetime  + timedelta(days = int(e.details['days after planting'])))
                
            
            #is it a harvesting step?
            harvest_step = -1
            print(e.details['is harvest step'])
            try:
                harvest_step = int(e.details['is harvest step'])
                
            except: 
                harvest_step = -1 
                
            if harvest_step >= 0:
                for i, stage in enumerate(self.simdf['Stage']):
                    if int(stage) == 0:
                        planned_datetime  = self.simdf['dateobject'].loc[i]
                        e.details['planned_timestamp']  = datetime.timestamp( planned_datetime ) + harvest_step
                        break
                        
                
                
            #is it tied to a specific gdd?
            gdd = -1
            try: 
                gdd = float( e.details['growing degree days after planting'])
            except:
                gdd = -1
            if gdd >= 0 :
                print("gdd event!!!" , gdd , self.simdf['GD'])
                gddsum = 0
                # ~ if int(e.details['growing degree days after planting']) >=0 
                for i, g in enumerate(self.simdf['GD']):
                    gddsum += g
                    if gddsum >= gdd:
                        planned_datetime  = self.simdf['dateobject'].loc[i]
                        e.details['planned_timestamp']  = datetime.timestamp( planned_datetime )
                        break
                
        #sort events list
        
        self.event_list.sort(key=lambda x: x.computer_details['planned_timestamp'], reverse=False)

                
    def print_plan(self):
        print( "cultivar = " , self.cultivar.details["name"])
        print(self.details)
        for e in self.event_list:
            e.pretty_print()
        return
            
    # ~ def fill_events_from_dir(self , path , cultivar ):
        # ~ #look at all .csv files in this dir, try to load them as events. 
        # ~ filepathlist = (glob.glob(path + "*.csv"))
        # ~ for f in filepathlist:
            # ~ try: 
                # ~ event = crop_event()
                # ~ event.load_from_csv( f)
            # ~ except:
                # ~ print("couldn't read data file " + f )
                # ~ pass 
            # ~ self.event_list.append(event)
        
       
        # ~ self.details['cultivar'] = cultivar.name
        # ~ self.details['soil_plot_ids'] = [] #each soil plot has an area, so this is how to figure out how much we are planting
        # ~ self.details['location'] = "placename" #no spaces or special characters here, used as a file name part
        # ~ self.details['cropfile.CRO'] = cultivar.cropfilename
        # ~ self.details['irrigation.IRR'] = "(NONE)" 
        # ~ self.details['minimum_harvest_temperature'] = cultivar.minimum_harvest_temperature
        # ~ self.details['death_temperature'] = cultivar.death_temperature
        # ~ self.details['cultivar_class'] = cultivar
        # ~ return
        
    def add_soil_ids(self , id_list):
        self.details['soil_plot_ids'] =id_list
        for e in self.event_list:
            e.details['soil_plot_ids'] =id_list
        return




