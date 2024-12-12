
from farm_data import * 



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
s1.details['area_m2'] = 1

###setup the whole farm 
Farm = farm_data()
Farm.soil_plot_dict['id0']=(s1)
dt = datetime(2024,3,25)
Farm.weather.last_observed_time = dt.timestamp() 
Farm.weather.fill_with_prediction(365, True)

saladbowl = cultivar()
saladbowl.name  = "saladbowl"
saladbowl.cropfilename = "saladbowl3.CRO" 
saladbowl.species = "lactuca sativa"
saladbowl.minimum_harvest_temperature = 0
saladbowl.death_temperature = -2

salad_plan = crop_plan()
salad_plan.fill_events_from_dir("./lettuce_event_templates_unit_test/" , saladbowl)
salad_plan.add_soil_ids( ['id0'] )
salad_plan.print_plan()



##optimiser 3 
opt3 = optimizer3(Farm , saladbowl, salad_plan)
dts = datetime(2024,3,25)
dte = datetime(2024,12,30)# make sure you predicte the future weather well beyond this dte so that the last sim has data to run on.
opt3.startdate = dts 
opt3.enddate = dte 

#make allowed harvest and planting bool vectors and test them:
opt3.setup_allowed_harvest_planting_dates()

print( opt3.enddate , opt3.dates[-1])
print( opt3.startdate , opt3.dates[0])
assert( opt3.enddate == opt3.dates[-1])
assert( opt3.startdate == opt3.dates[0])
assert( opt3.startdate + timedelta(days = 1) == opt3.dates[1])
#ok so now the dates should be right
assert( opt3.ndates == len(opt3.dates)) 
assert( opt3.ndates == len(opt3.harvest_dates_bool)) 
assert( opt3.ndates == len(opt3.planting_dates_bool)) 
#sizes ok
print( ) 
print( opt3.planting_dates_bool) 
print( "date 5 is " , opt3.dates[5] )
print( opt3.dates_dict[ opt3.dates[5] ]  , " should be 5 too")
assert( opt3.dates_dict[ opt3.dates[5] ]  == 5 )
#the going between dates and index works 

opt3.setup_temperatures()
assert( opt3.Tmax[   opt3.dates_dict[ opt3.dates[0] ]   ] == Farm.weather.df_predict['Tmax(C)'].loc[dts] )
print( opt3.Tmin[0] , " temp on first day")

#ok now do the sims 


if False:
    opt3.do_aquacrop_sims()
    with open('testopt3.pickle', 'wb') as handle:
        pickle.dump( opt3 , handle, protocol=pickle.HIGHEST_PROTOCOL)
if True:
    #reload from pickle all the sims 
    with open('testopt3.pickle', 'rb') as handle:
        opt3 = pickle.load(handle)

print( opt3.list_of_sim_dfs[21]) 
print( opt3.list_of_Y_dicts[21]) 

opt3.trim_planting_bool_for_weather()
assert( opt3.planting_dates_bool[0] == 0)
assert( opt3.planting_dates_bool[3] == 0)
assert( opt3.planting_dates_bool[7] == 0)

print(opt3.planting_dates_bool)

i,area = opt3.find_planting_area( 84 , 1)
assert  ( abs(area -  1.0/3.8993)  < 0.001) 
assert  ( i==21) 
print ( opt3.find_planting_area( 87 , 1) )
