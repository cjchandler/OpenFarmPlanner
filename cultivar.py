#cultivar class 
import json

class cultivar:
    def __init__(self):
        self.details = {}
        self.details['name']  = "saladbowl"
        self.details['cropfilename'] = "saladbowl3.CRO" 
        self.details['species'] = "lactuca sativa"
        self.details['minimum_harvest_temperature'] =0 
        self.details['death_temperature'] = 0 
        self.details['shelf_life_post_harvest'] = 3 
        self.details['post_harvest_storage_instructions'] = 'keep at 4c'
        self.details['gdd_threshold_for_early_harvest'] = 0.8 #as in you can start harvesting at 80% of the growing degree days 
        self.details['aquacrop_gdd_at_mature'] = 432
        
     
    def dump_to_json(self ,path ):
        #look in path, is there an 
        filename = self.details['name'] + "_cultivar.json"
        out_file = open(path+"/"+filename, "w")

        json.dump(self.details, out_file, indent = 6)

        out_file.close()
        
        #then dump all the events in event list... 
 
    def load_from_json(self , filename):
        with open(filename) as f:
            self.details = json.load(f)


