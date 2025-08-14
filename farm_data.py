# farm planner farm class 
import time
from datetime import datetime, timedelta
import json
from weather import * 
from crop_plan import * 

class farm_data:
    def __init__(self):
        self.details={}
        self.details['farm_address'] = "South Ohio, NS"
        self.details['farm_name'] = "TestFarm"
        self.details['last_observed_weather_day' ] =25
        self.details['last_observed_weather_month' ] = 1 
        self.details['last_observed_weather_year' ] = 2025
        
        dt = datetime(self.details['last_observed_weather_year' ],self.details['last_observed_weather_month' ],self.details['last_observed_weather_day' ] )
        self.weather = weather()
        self.weather.last_observed_time = dt.timestamp() 
        self.weather.load_observed_weather()
        self.weather.fill_with_prediction(365, True) 
        
        self.soil_plot_dict = {} #id is key, value is soil_plot class instance
        self.active_crop_plan_list = []
        self.past_crop_plan_list = []


    def dump_self_details_to_json(self ,path ):
        #look in path, is there an 
        filename = "farm_details.json"
        out_file = open(path+"/"+filename, "w")

        json.dump(self.details, out_file, indent = 6)

        out_file.close()
        
 
    def load_self_details_from_json(self , path_to_crop_plan_dir):
        path = path_to_crop_plan_dir
        
        ##get the details, that's easy 
        with open(path+"/farm_details.json" ) as f:
            self.details = json.load(f)

    def dump_to_json(self ,path ):
        ##make a folder, with a unique name
        farm_dir = self.details['farm_name'] + "_" + str(int(time.time()))
        os.makedirs(path + farm_dir )
        
        self.dump_self_details_to_json( path + farm_dir)
        
        ##make a dir for active crop plans
        os.makedirs(path + farm_dir + "/active_crop_plans")
        for cp in self.active_crop_plan_list:
            cp.dump_to_json(path + farm_dir + "/active_crop_plans/")
        
        ##make a dir for active crop plans
        os.makedirs(path + farm_dir + "/past_crop_plans")
        for cp in self.past_crop_plan_list:
            cp.dump_to_json(path + farm_dir + "/past_crop_plans/")
        
        #make a dir for soil plots
        os.makedirs(path + farm_dir + "/soil_plots")
        for key, value in self.soil_plot_dict.items():
            value.dump_to_json(path + farm_dir + "/soil_plots/")
       
        
        return path + farm_dir
        
    def load_recent_from_json(self , path):
        ##find the most recent farm dir 
        farmfiles = []
        farm_n = []
        for filename in glob.glob(path +self.details['farm_name']+"*"):
            farmfiles.append(filename)
            a=filename.split("_")
            farm_n.append( int(a[-1]))
        
        n = max(farm_n)
        path = path +self.details['farm_name']+"_"+ str(n) + "/"
        
        #load farm details
        self.load_self_details_from_json(path)
        
        #now load active crop plans
        cropplans = []
        for filename in glob.glob(path + "active_crop_plans/**"):
            cropplans.append(filename)
            # ~ print(filename)
        for cpname in cropplans:
            cptemp = crop_plan()
            
            outtest = cptemp.load_crop_plan_from_dir( cpname)
            # ~ print("loading a crop plan---", outtest)
            # ~ cptemp.print_plan()
            
            self.active_crop_plan_list.append( cptemp)
            
        
        #now load past crop plans
        cropplans = []
        for filename in glob.glob(path + "past_crop_plans/**"):
            cropplans.append(filename)
        for cpname in cropplans:
            cptemp = crop_plan()
            cptemp.load_crop_plan_from_dir( cpname)
            self.past_crop_plan_list.append( cptemp)
        
        #get soil plots 
        ##now get the events
        soilfiles = []
        
        for filename in glob.glob(path + "soil_plots/*soil_plot.json"):
            soilfiles.append(filename)
            # ~ print(filename)
        for sp in soilfiles:
            sptemp = soil_plot()
            sptemp.load_from_json( sp)
            # ~ print( "------ loading soil-----")
            # ~ print(sptemp.details)
            # ~ print( sptemp.details['id'] )
            # ~ print( "------ loading soil-----")

            self.soil_plot_dict[sptemp.details['id']] = ( sptemp)
        
        
        
        
        
        
        
        
