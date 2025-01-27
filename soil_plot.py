import time
import json

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
        
    def dump_to_json(self ,path ):
        #look in path, is there an 
        filename = self.details['id'] + "_soil_plot.json"
        out_file = open(path+"/"+filename, "w")

        json.dump(self.details, out_file, indent = 6)

        out_file.close()
        
        #then dump all the events in event list... 
 
    def load_from_json(self , filename):
        with open(filename) as f:
            self.details = json.load(f)
