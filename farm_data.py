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
         
        
class crop_event:
    def __init__(self):
        self.details = {}
        self.details['event_name'] = " "
        self.details['human_instructions'] = " "
        self.details['time_estimate_min'] = 0
        self.details['time_taken_min'] = -1
        self.details['soil_plot_list'] =  [] 
