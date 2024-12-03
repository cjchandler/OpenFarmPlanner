import geopy
import geopy.distance
import numpy as np
import pandas as pd
import time
from datetime import datetime, timedelta
from aquacrop import aquacrop_wrapper
import pprint
import pickle

def dump_farm_data( f):
    dtn = datetime.now()
    filename = f.farm_name + "_farm_state.pickle"
    with open(filename, 'wb') as handle:
        pickle.dump(f, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_farm_data(f):
    dtn = datetime.now()
    filename = f.farm_name + "_farm_state.pickle"
    with open(filename, 'rb') as handle:
        b = pickle.load(handle)
    return b




def date_string_to_timestamp( datestring):
    l = datestring.split('-')
    dt= datetime(int(l[2]), int(l[1]) , int(l[0]) )
    timestamp = (dt - datetime(1970, 1, 1)) / timedelta(seconds=1)
    return timestamp

def timestamp_to_date( ts):
    dt_object = datetime.fromtimestamp(timestamp)
    return str(dt_object.day) + '-' + str(dt_object.month) + '-' + str(dt_object.year)


    

class weather:
    def __init__(self):
        self.last_observed_time = 0 #this is timestamp for the last actual data we have, after that it's all prediction
        self.df_daily = pd.DataFrame() #this is observed and forcast weather all in a lump so we can run the crop model 
        self.df_observed = pd.DataFrame() #real weather as observed
        #weather df format:[ 'Day', 'Month' , 'Year' , 'Tmin(C)' , 'Tmax(C)' , 'Prcp(mm)' , 'ET0']
        self.df_predict = pd.DataFrame()
        
    def load_observed_weather(self):
        self.df_observed = pd.read_csv('./localWeatherData/climate_ofp.csv') 
        self.df_observed['Datetime'] = pd.to_datetime(self.df_observed['Datetime'])
        self.df_observed = self.df_observed.set_index('Datetime') 
        
    def fill_with_prediction( self, ndays):
        #look at the observed weather and guess at the future weather
        last_datetime = datetime.fromtimestamp( self.last_observed_time)
        self.df_observed = self.df_observed.loc[:last_datetime]
        
        print(self.df_observed)

       
        
        #make a range of dates into the future 
        datelist = pd.date_range(last_datetime, periods=ndays)
        print(datelist)
        
        listdeltas= []
        for a in range( 1 , 11):
            listdeltas.append( pd.Timedelta(days=a*365) )
        
        df = pd.DataFrame(columns=self.df_observed.columns.values, index=datelist)
        
        for d in datelist:
            Tmin = []
            Tmax = []
            ET0 = []
            prcp =[]
            #look at the past 10 years on this date: 
            #make a list of the rows we get: 
            rowlist = []
            for bdelta in listdeltas:
                
                ET0.append (self.df_observed['ET0'].loc[d - bdelta])
                prcp.append (self.df_observed['Prcp(mm)'].loc[d - bdelta])
                Tmax.append (self.df_observed['Tmax(C)'].loc[d - bdelta])
                Tmin.append (self.df_observed['Tmin(C)'].loc[d - bdelta])
            # ~ Datetime,Day,Month,Year,Tmin(C),Tmax(C),Prcp(mm),ET0
            
            df.loc[d] = pd.Series({'Day':d.day, 'Month':d.month, 'Year':d.year, 'Tmin(C)':np.mean(Tmin) , 'Tmax(C)':np.mean(Tmax), 'Prcp(mm)':np.mean(prcp) , 'ET0':np.mean(ET0) })
            
            # ~ print(np.mean(ET0))
    
        dfout = pd.concat( [self.df_observed, df])
        print(dfout)
        idstr = str(self.df_observed.index[-1].day) + '-' +str(self.df_observed.index[-1].month) + '-' + str(self.df_observed.index[-1].year)
        dfout.to_csv('predicted_' + idstr+ '_climate_ofp.csv')
        self.df_predict = dfout


# farm planner farm class 
class farm_data:
    def __init__(self):
        self.farm_address = "South Ohio, NS"
        self.farm_name = "TestFarm" 
        self.soil_plot_list = []
        self.active_crop_plan_list = []
        self.weather = weather()
        self.weather.load_observed_weather()
        
        
        
        
        #archive data? 
            #we will need a way to get this all together from file when we need it 
            
        #economic information, what are the seaonal demand curves looking like for each crop?

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
        self.details['soil_plot_ids'] = [] #each soil plot has an area, so this is how to figure out how much we are planting
        self.details['location'] = "placename" #no spaces or special characters here, used as a file name part
        self.details['cropfile.CRO'] = "saladbowl3.CRO" 
        self.details['irrigation.IRR'] = "(NONE)" 
        self.details['minimum_harvest_temperature'] = 0
        self.details[''] = " " 
        self.simdf = pd.DataFrame()
    
         
    def make_all_events(self):
        #well obviosly there needs to be a data base of how to do each crop. 
        #then we also can look back at other times we did this crop
        
        print("This is setting up the crop plan. What is the cultivar name?")
        n = input()
        self.details['cultivar'] = lower(n) 

        

    def set_event_times(self , planting_datetime , df_predict):
        
        df_predict['datetime'] = pd.to_datetime(df_predict[['Year', 'Month', 'Day']]) 
        self.simdf = aquacrop_wrapper.simAquaCrop(  self.details['location'], "./aquacrop" , planting_datetime , df_predict['datetime'].iloc[-1] ,  df_predict , self.details['minimum_harvest_temperature'] , self.details['cropfile.CRO'] , self.details['irrigation.IRR']) 
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
                e.computer_details['planned_timestamp'] = datetime.timestamp(planting_datetime  + timedelta(days = int(e.details['days after planting'])))
                
            
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
                        e.computer_details['planned_timestamp']  = datetime.timestamp( planned_datetime ) + harvest_step
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
                        e.computer_details['planned_timestamp']  = datetime.timestamp( planned_datetime )
                        break
                
        #sort events list
        
        self.event_list.sort(key=lambda x: x.computer_details['planned_timestamp'], reverse=False)

                
    def print_plan(self):
        for e in self.event_list:
            e.pretty_print()
            
           

        
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
        self.details['days after planting'] = 'q'
        self.details['growing degree days after planting'] = 'q'
        self.details['is harvest step'] = -1 #-1 or '' is before harvesting. 0 is first harvest step, 1 is next etc  
        
        self.computer_details = {} #this is stuff that the farmer should never have to adjust manually in .csv 
        self.computer_details['planned_timestamp'] = 0 
        self.computer_details['actual_timestamp_start'] = ' ' 
        self.computer_details['actual_timestamp_end'] = ' ' 
 
    
    def pretty_print(self):
        planneddt = datetime.fromtimestamp(self.computer_details['planned_timestamp'])
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



CE = crop_event()
CE.save_as_csv("my_test_event.csv")
CE.load_from_csv("./lettuce_event_templates/plant_lettuce_event.csv")
 

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

lettuce_plan.event_list = [ soil_prep , planting , weeding, harvesting , post_harvesting] 
#so these are all the events, but they don't have any times associated with them 

#now I load the weather so I can work on time and simulations 
W = weather()
dt = datetime(2024,3,25)
W.last_observed_time = dt.timestamp() 
W.load_observed_weather()
        
W.fill_with_prediction(360)


#back to crop plan 
lettuce_plan.set_event_times( dt, W.df_predict)

lettuce_plan.print_plan()


###setup the whole farm 
Farm = farm_data()
Farm.soil_plot_list.append(s1)
Farm.active_crop_plan_list.append(lettuce_plan)
dump_farm_data(Farm)

Farm = load_farm_data(Farm)
Farm.active_crop_plan_list[0].print_plan()
