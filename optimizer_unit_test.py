
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

opt = optimizer(Farm , saladbowl, salad_plan)
dts = datetime(2024,3,25)
dte = datetime(2024,12,30)
# ~ opt.optimize_cultivar( dts  , dte) # make sure you predicte the future weather well beyond this dte so that the last sim has data to run on.

opt.startdate = dts 
opt.enddate = dte 

##optimiser 2 
opt2 = optimizer2(Farm , saladbowl, salad_plan)
dts = datetime(2024,3,25)
dte = datetime(2024,12,30)# make sure you predicte the future weather well beyond this dte so that the last sim has data to run on.
opt2.startdate = dts 
opt2.enddate = dte 
opt2.setup_allowed_harvest_dates()
if True:
    print(opt2.allowed_harvest_dates)

if False:
    opt2.do_aquacrop_sims()
    # ~ print( opt2.list_of_sim_dfs)
    with open('testopt3.pickle', 'wb') as handle:
        pickle.dump( opt2 , handle, protocol=pickle.HIGHEST_PROTOCOL)
if True:
    #reload from pickle all the sims 
    with open('testopt3.pickle', 'rb') as handle:
        opt2 = pickle.load(handle)
     
    print( opt2.find_best_planting_date( opt2.list_of_sim_dfs, datetime( 2024 , 6 , 6)))

if True:
    opt2.set_constant_demand(1)
    plant_bool = np.zeros( opt2.ndates)
    harvest_bool = np.zeros( opt2.ndates)
    
    f = 20
    harvest_bool[101+f] = 1 
    harvest_bool[103+f] = 1 
    harvest_bool[106+f] = 1 
    
    plant_bool[81+ f] = 1 
    plant_bool[82+f] = 1 
    plant_bool[84+f] = 1 
    
    plant_area = opt2.find_planting_areas( plant_bool , harvest_bool)
    print(plant_area)
    

if True: 
    opt2.make_yield_matrix()
    print( opt2.H)
    
    print( opt2.estimate_labour_for_crop())
    
    print( opt2.estimate_labour_for_crop_Matrix(plant_area) , "labour min" ) 
    
    
    print( opt2.estimate_sales( opt2.H.dot(plant_area) ) , "kg sales")



















quit()
##optimiser 1 
if False: #test making matrix from sim yields
    opt.make_yield_matrix()
    ###ok, now lets test it, by planting 1 m2 area every day
    planting_test_vec = np.ones( len(opt.dates))
    yields = opt.H.dot(planting_test_vec)
    print( sum(yields) ) 
    print( opt.H.sum())
    assert( abs( sum(yields) - opt.H.sum() ) < 0.01)

    print( opt.estimate_labour_for_crop_Matrix( planting_test_vec  ) )

if False: #test making matrix, then pickle it for testing faster
    #make and pickle the sims setup:
    opt.make_yield_matrix()
    ###ok, now lets test it, by planting 1 m2 area every day
    planting_test_vec = np.ones( len(opt.dates))
    yields = opt.H.dot(planting_test_vec)
    with open('testopt.pickle', 'wb') as handle:
        pickle.dump( opt , handle, protocol=pickle.HIGHEST_PROTOCOL)

if False: #test the estimation of sales from demand and yield
    #reload from pickle all the sims 
    with open('testopt.pickle', 'rb') as handle:
        opt = pickle.load(handle)

    #now look at the cost estimate
    opt.set_constant_demand(1)
    planting_test_vec = np.ones( len(opt.dates))
    yields = opt.H.dot(planting_test_vec)
    print(opt.estimate_sales(  yields))
    opt_areas = opt.optimize_cultivar( dts  , dte)
    print(  opt.H.dot(opt_areas) )
    print(opt.estimate_sales(  opt.H.dot(opt_areas)))
    
    with open('testopt2.pickle', 'wb') as handle: ###dump after optimization
        pickle.dump( opt , handle, protocol=pickle.HIGHEST_PROTOCOL)

if False:
    #reload from pickle all the sims 
    with open('testopt2.pickle', 'rb') as handle:
        opt = pickle.load(handle)
    
    #plot demand, harvest, sales per day

if False:
    opt.set_constant_demand(1)#set demand to 1 kg per day, every day  
    opt.optimize_cultivar( dts  , dte)

