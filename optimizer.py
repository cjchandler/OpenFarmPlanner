import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from aquacrop import aquacrop_wrapper
import collections
from scipy.optimize import minimize, rosen, rosen_der
from scipy.optimize import basinhopping, differential_evolution
import itertools
import random

class optimizer3:
    def __init__(self , fd , cultivar, sample_crop_plan):
        self.cultivar= cultivar
        self.farm_data = fd
        self.sample_crop_plan = sample_crop_plan
        self.startdate = datetime(1901,1,1)
        self.enddate = datetime(1901,1,1)
        
        self.harvest_dates_bool = []
        self.planting_dates_bool = []
        self.dates=[]
        self.ndates = 0 
        self.dates_dict = {}
        self.Tmax = []
        self.Tmin = []
        self.list_of_sim_dfs = []
        self.list_of_Y_dicts = [{} , {}]
        self.demand = [] #kg produce that can be sold per day 
        self.min_yield_fraction = 0.2 #this means that if a planting is projected to yeild below this fraction of the largest modelled harvest, it's not worth planting
        #we need this to avoid planting in the middle of the winter if there is a stretch of 5 days above zero or something.

        self.planting_areas = []
        self.n_plantings_on_this_day = []
        

    def setup_allowed_harvest_planting_dates(self):
        self.dates = pd.date_range(start= self.startdate, end=self.enddate  , freq='D').to_list()
        self.ndates = len(self.dates)
        
        d1 = pd.date_range(self.startdate, self.enddate, freq="W-MON")
        d2 = pd.date_range(self.startdate,  self.enddate, freq="W-THU")

        self.allowed_harvest_dates = d1.union(d2)
        
        self.harvest_dates_bool =np.zeros( self.ndates )
        
        for i , val in enumerate(self.harvest_dates_bool):
            self.dates_dict[ self.dates[i]  ]= i
            if self.dates[i] in self.allowed_harvest_dates:
                self.harvest_dates_bool[i]  = 1
    
        self.planting_dates_bool = list(self.harvest_dates_bool)
        
    def setup_temperatures(self):
        #find weather df index for the start date:
        
        
        for i , day in enumerate( self.dates):
            self.Tmax.append(self.farm_data.weather.df_predict['Tmax(C)'].loc[day])
            self.Tmin.append(self.farm_data.weather.df_predict['Tmin(C)'].loc[day])
        
        
    def do_aquacrop_sims(self):
        #populate self.dates
        self.dates = pd.date_range(start= self.startdate, end=self.enddate  , freq='D').to_list()
        self.ndates = len(self.dates)
        
        #sim all these dates if the temperature makes sense:
        self.list_of_sim_dfs = [pd.DataFrame()]* self.ndates
        self.list_of_Y_dicts = [ {} ]* self.ndates
        # ~ print(self.farm_data.weather.df_predict)
        # ~ print(self.farm_data.weather.df_predict.loc[ datetime(2024,3,15) : datetime(2024,3,30) ] )

        for i, dt in enumerate(self.dates):
            #is it too cold to plant? 
            min_temp = self.Tmin[i]
            
            print(min_temp , "min temp")
            if min_temp <= self.cultivar.death_temperature:
                pass
                self.list_of_Y_dicts[i] = {i: -1 }
            else:
                df= aquacrop_wrapper.simAquaCrop(  'plansim', "./aquacrop" , dt , self.farm_data.weather.df_predict['datetime'].iloc[-2] ,  self.farm_data.weather.df_predict , self.cultivar.minimum_harvest_temperature, self.cultivar.cropfilename , self.sample_crop_plan.details['irrigation.IRR']) 
                self.list_of_sim_dfs[i] = df 
                df['dateobject']
                Y_dict = {}
                for a in range( 0 , len(df.index)):
                    Y_dict[a + i] = df['Y(fresh)'].iloc[a]*1000/10000 #this units thing is so we get kg/m2 not ton per hectacre
                    
                self.list_of_Y_dicts[i] = Y_dict
                
                
        return
    
    def set_constant_demand(self , kg_per_day):
        self.demand = np.ones(self.ndates)*kg_per_day
    
    def trim_planting_bool_for_weather(self):
        #what is max yield? 
        max_Y = 0 
        for Y_dict in self.list_of_Y_dicts:
            i = max(Y_dict, key=Y_dict.get)
            Y = Y_dict[i]
            if Y > max_Y:
                max_Y = Y 
                
        for i, p_val in enumerate(self.planting_dates_bool):
            Y_dict = self.list_of_Y_dicts[i] 
            j = max(Y_dict, key=Y_dict.get)
            Y = Y_dict[j] #this is the yield for this planting
            if Y < max_Y*self.min_yield_fraction:
                self.planting_dates_bool[i] =0 

    
    def find_planting_area(self, i , demand):#find area to plant and day index to plant for this demand and harvest index i 
        planting_index = -1
        productivity = - 1
        if self.harvest_dates_bool[i] == 1:
            #look through all the sims for the one with a harvest index higher than this i, which is also a planting date 
            for a in range(0 , i):
                Y_dict = self.list_of_Y_dicts[a]
                sim_harvest_index = max( Y_dict)
                if sim_harvest_index >= i and self.planting_dates_bool[a] > 0 :
                    planting_index = a
                    productivity = Y_dict[i]
                    break
        
            #ok so now we have a planting index and a productivity
            if productivity <= 0: #but it doesn't work if productivity ==0 
                return -1 , -1 
                
            area = demand/productivity
            return planting_index , area
        else:
            return -1 , -1 
    
    def find_all_planting_areas( self):
        shelf_life = self.sample_crop_plan.details['cultivar_class'].shelf_life_post_harvest
        self.planting_areas = np.zeros(self.ndates)
        self.n_plantings_on_this_day = np.zeros(self.ndates)
        
        for ih, h_val in enumerate(self.harvest_dates_bool):
            if h_val == True: 
                try:
                    demand = sum( self.demand[ih-shelf_life: ih])
                except:
                    demand = 0 
                ip , area = self.find_planting_area(ih , demand)  
                if ip >= 0 and area > 0:
                    self.planting_areas[ip] += area 
                    self.n_plantings_on_this_day[ip] += 1 
                     
            








































class optimizer2:
    def __init__(self , fd , cultivar, sample_crop_plan):
        self.cultivar= cultivar
        self.farm_data = fd
        self.yield_vec = [1 ,1] #how much yield in kg from a crop planted on day this index represents as in self.dates
        self.demand_kg_per_day = [ 1 , 1]
        # ~ self.yield_kg_per_day = [ 0 , 0]
        self.dates = [ datetime(1901,1,1) , datetime(1901,1,2) ]#one date for every sim day we are optimizing over
        self.optimum_planting_areas = [ 1.4 , 1]
        self.sales = [ 1 , 1] #how much we can sell each day. never higher than demand
        self.ndates = len(self.dates)
        self.demand = [ 1 , 1]#this is demand in kg per day for each of the self.dates  
        self.demand_forcing_intensity = 0.1
        self.labour_constant_min = 10
        self.labour_min_per_m2 = 60
        self.startdate = datetime(1901,1,1)
        self.enddate = datetime(1901,1,1)
        self.sample_crop_plan = sample_crop_plan
        self.H = np.zeros([2,2]) #yield or harvest matrix

        self.allowed_harvest_dates = []
        self.harvest_dates_bool = []
        self.list_of_sim_dfs = []
        
        self.max_area = 1e32 #this is to kill areas that are too large to be reasonable, inf that wrecks optimisation
        
        
    def setup_allowed_harvest_dates(self):
        self.dates = pd.date_range(start= self.startdate, end=self.enddate  , freq='D').to_list()
        self.ndates = len(self.dates)
        
        d1 = pd.date_range(self.startdate, self.enddate, freq="W-MON")
        d2 = pd.date_range(self.startdate,  self.enddate, freq="W-THU")

        self.allowed_harvest_dates = d1.union(d2)
        
        self.harvest_dates_bool =np.zeros( self.ndates )
        
        for i , val in enumerate(self.harvest_dates_bool):
            if self.dates[i] in self.allowed_harvest_dates:
                self.harvest_dates_bool[i]  = 1
        
    
    def do_aquacrop_sims(self):
        #populate self.dates
        self.dates = pd.date_range(start= self.startdate, end=self.enddate  , freq='D').to_list()
        self.ndates = len(self.dates)
        
        #sim all these dates if the temperature makes sense:
        self.list_of_sim_dfs = [pd.DataFrame()]* self.ndates
        # ~ print(self.farm_data.weather.df_predict)
        # ~ print(self.farm_data.weather.df_predict.loc[ datetime(2024,3,15) : datetime(2024,3,30) ] )

        for i, dt in enumerate(self.dates):
            #is it too cold to plant? 
            min_temp = ( self.farm_data.weather.df_predict['Tmin(C)'].loc[dt])
            print(min_temp , "min temp")
            if min_temp <= self.cultivar.death_temperature:
                pass
            else:
                self.list_of_sim_dfs[i] = aquacrop_wrapper.simAquaCrop(  'plansim', "./aquacrop" , dt , self.farm_data.weather.df_predict['datetime'].iloc[-2] ,  self.farm_data.weather.df_predict , self.cultivar.minimum_harvest_temperature, self.cultivar.cropfilename , self.sample_crop_plan.details['irrigation.IRR']) 


    def make_yield_matrix(self):
        
        
        yieldF = np.zeros(self.ndates) # the yieldF[i] is yeild for crop planted on date index i 
        harvest_dates = [datetime(1901,1,1)]*self.ndates
        harvest_date_index = np.zeros(self.ndates)
        print(yieldF)

        for i, dt in enumerate(self.dates):
            yieldF[i] = 0 
            if( len(self.list_of_sim_dfs[i].index)>=1): 
                yieldF[i] = self.list_of_sim_dfs[i]['Y(fresh)'].iloc[-1]*1000/10000 #this units thing is so we get kg/m2 not ton per hectacre
                
                harvest_dates[i] = self.list_of_sim_dfs[i]['dateobject'].iloc[-1]
                try: 
                    harvest_date_index[i] = int(self.dates.index(harvest_dates[i]))
                    # ~ print(type(harvest_date_index[i]))
                except: 
                    #didn't have that date in our list, it's probably too far in the future to consider , so just put 0, that will ignore this yeild  
                    harvest_date_index[i] = 0
        print(harvest_date_index)
        
        #for matrix M[b,a]= Y , Y is kg produce, b is harvest date, a is planting date 
        self.H = np.zeros([self.ndates , self.ndates])
        self.yield_vec = yieldF
        for i, y in enumerate(yieldF):
            b = int(harvest_date_index[i])
            a = i 
            if( b != 0 and b <self.ndates):
                self.H[ b, a] = y
                
        print(self.H)



    def set_constant_demand(self , kg_per_day):
        self.demand = np.ones(self.ndates)*kg_per_day

    def find_best_planting_date( self , input_sim_df_list , harvest_date ):
        closest_date = datetime(1901, 1,1 )
        closest_index = -1 
        for i, df in enumerate(input_sim_df_list):
            
            if len(df.index) > 0 :
                #look at the sim df dates.
                # ~ print( harvest_date, "harvest date" , "sim range" ,  df['dateobject'].iloc[0] ,  df['dateobject'].iloc[-1] )
                 
                if harvest_date > df['dateobject'].iloc[0] and harvest_date < df['dateobject'].iloc[-1]: #then we can use this planting date potentially
                    
                    this_harvest_date = df['dateobject'].iloc[-1]
                    # ~ print(this_harvest_date)
                    # ~ print( abs(this_harvest_date.timestamp() - harvest_date.timestamp()) )
                    
                    if abs(this_harvest_date.timestamp() - harvest_date.timestamp()) <  abs(closest_date.timestamp() - harvest_date.timestamp() ) :
                        closest_date = this_harvest_date
                        closest_index = i 
                        
                        
        # ~ print( closest_index , "closest_index" ) 

        if closest_index >= 0 :
            #ok, so now I know the best sim
            planting_date = input_sim_df_list[closest_index]['dateobject'].iloc[0]
            # ~ print( " planting_date" , planting_date)
            
            
            sim_timestamp_list = input_sim_df_list[closest_index]['timestamp'].to_numpy()
            # ~ print(sim_timestamp_list)
            #ok this finds the index of the timestamp in the sim output that is the harvest date we have specified. The crop may not be mature but we harvest regardless
            harvest_df_index = min(range(len(sim_timestamp_list)), key=lambda i: abs(sim_timestamp_list[i]-  harvest_date.timestamp() ))
            # ~ print( "harvest_df_index" , harvest_df_index)


            harvest_kg_per_m2 = input_sim_df_list[closest_index]['Y(fresh)'].iloc[harvest_df_index]*1000/10000 #this units thing is so we get kg/m2 not ton per hectacre
            # ~ print( "harvest_kg_per_m2" , harvest_kg_per_m2)
            planting_date_i = self.dates.index( planting_date )


        if closest_index == -1:
            #no solution
            planting_date= datetime(1901, 1,1 ) 
            harvest_kg_per_m2  = 0 
            planting_date_i = -1
                #look at yield
        
        # ~ print(planting_date_i, planting_date , harvest_kg_per_m2 , "planting_date_i, planting_date , harvest_kg_per_m2")
        return planting_date_i, planting_date , harvest_kg_per_m2
    
    
    
    def find_planting_areas( self , planting_dates_bool , harvest_dates_bool):
        #list of allowed planting sims 
        allowed_sims = []
        planting_areas = np.zeros(self.ndates)
        shelf_life = self.sample_crop_plan.details['cultivar_class'].shelf_life_post_harvest

        
        for i, dt in enumerate(self.dates):
            
            if( planting_dates_bool[i] == True ):
                allowed_sims.append( self.list_of_sim_dfs[i])
                
            if( harvest_dates_bool[i] == True ):
                #find best planting date
                plantdt_index , plantdt , harvest_per_m2 = self.find_best_planting_date( allowed_sims, self.dates[i])
                if plantdt_index < 0:
                    pass #don't plant anything there is no way to do it. 
                else:
                    storable_demand = 0 
                    for a in range( 0 , shelf_life):
                        storable_demand += self.demand[i+a]
                    
                    planting_areas[ plantdt_index ] = storable_demand/harvest_per_m2 
            
        
        for i , val in enumerate(planting_areas):
            if val > self.max_area: 
                planting_areas[i] = 0 
            
        return planting_areas 
        
    def estimate_labour_for_crop(self  ):
        crop_plan = self.sample_crop_plan
        #give a constan time for this crop, and a time per m2 
        
        
        #if there are events in past crop plans with the same description, worker id as the proposed ones,
        #make a list of mean_past_events where each event has a mean time scaled by area
        if ( len(self.farm_data.past_crop_plan_list) > 0 ): 
            self.farm_data.mean_past_events = [ self.past_crop_plan_list[0].event_list[0] ]
            for past_crop_plan in self.farm_data.past_crop_plan_list:
                for pe in past_crop_plan:
                #check if pe is in mean_past_events. 
                    for me in mean_past_events:
                        if pe.compare_events(me) == True:
                            #update the mean, add the area aka soil plot ids and add and time_taken_min
                            me.details['time_taken_min'] = me.details['time_taken_min'] + pe.details['time_taken_min'] 
                            me.details['soil_plot_ids'] = me.details['soil_plot_ids']  + pe.details['soil_plot_ids'] 
                        else:
                            mean_past_events.append(pe)

        #now look at the proposed events. crop_plan.event_list
        
        #now make a best time 'time_estimate_generated' for each of these events using either mean_past_events or calcualtion from human input
        # ~ print( len(joined_proposed_events) ) 
        # ~ joined_proposed_events[0].pretty_print() 
        
        area_time_min = 0
        constant_time_min = 0 
        switching_min = 2 #time cost to switch jobs  
        for e in crop_plan.event_list:
            area = 0 
            for sid in e.details['soil_plot_ids']:
                area+= self.farm_data.soil_plot_dict[ sid ].details['area_m2']
        
            e.details['time_estimate_generated']= switching_min + e.details['time_estimate_min_per_m2']*area
            area_time_min += e.details['time_estimate_min_per_m2']
            constant_time_min += switching_min
        
        self.labour_constant_min = constant_time_min
        self.labour_min_per_m2 = area_time_min
        
        return  constant_time_min, area_time_min
        
    def estimate_labour_for_crop_Matrix(self , area_vector  ):
        #give a time for this crop area vector 
        labour_time = 0
        for a in area_vector:
            if a > 0:
                labour_time += a*self.labour_min_per_m2 + self.labour_constant_min
        
        return labour_time
        
            
    def estimate_sales( self, harvest_vec):
        self.sales = np.zeros(self.ndates)
        #every day you potentially harvest some crop, and you sell some crop
        #you need to know how long you can hold the crop after harvesting. That's information in cultivar
        shelf_life = self.sample_crop_plan.details['cultivar_class'].shelf_life_post_harvest
        
        #so walk though the list with a deque of how much crop and how old it is in storage
        stock = collections.deque(maxlen=shelf_life)
        total_sold = 0 
        for i in range(0 , self.ndates ):
            today_demand = self.demand[i] 
            stock.append(harvest_vec[i])#add today's harvest, if there is any old harvest it gets dumped
            # ~ print("stock" , stock)
            for a, val in enumerate(stock):
                # ~ print("a" , a )
                if stock[a] >= today_demand:
                    sold =  today_demand
                    today_demand = today_demand - sold
                    stock[a] = stock[a] - sold
                    total_sold += sold
                    self.sales[i] += sold

                if stock[a] < today_demand:
                    sold =  stock[a]
                    today_demand = today_demand - sold
                    stock[a] = stock[a] - sold
                    total_sold += sold
                    self.sales[i] += sold
        
        return total_sold
  
    def vec_to_bool(self, v):
        for a in v:
            if a > 0.5:
                a = 1 
            else:
                a = 0
                 
        return v 
        
    def cost_func( self, planting_dates_bool): #input here is planting dates vector bool, optimal areas for that are calculated from sims and shelflife 
        # ~ planting_dates_bool = self.vec_to_bool(planting_dates_bool)
        # ~ print(planting_dates_bool)
        area_vector = self.find_planting_areas(  planting_dates_bool , self.harvest_dates_bool)
        
        area_vector = area_vector * (area_vector >= 0) #this sets all the negative areas to zero
        yield_vec = self.H.dot(area_vector)
        sold = self.estimate_sales( yield_vec) 
        time_labour = self.estimate_labour_for_crop_Matrix( area_vector) 
        print(-sold/(time_labour + 1e-8) , sold , time_labour )
        return -sold/(time_labour + 1e-8) #this kg sold/min of labour, obviously this needs to be maximized, use negative to minimize it
        
    # ~ def brute_force_opt( self , startdate , enddate):
        # ~ self.startdate = startdate
        # ~ self.enddate = enddate
        
        
        # ~ planting_best_bool = np.zeros(self.ndates)
        # ~ config = np.zeros(self.ndates)
        # ~ best_cost =0.0
        # ~ planting_bool = np.zeros(self.ndates)
        # ~ planting_allowed = np.zeros(self.ndates)
        # ~ s = self.sample_crop_plan.details['cultivar_class'].shelf_life_post_harvest
        # ~ for a, val in enumerate(planting_bool):
            # ~ if a%s == 0:
                # ~ planting_bool[a] = 1
                # ~ planting_allowed[a] = 1
        
        # ~ window_start_i = 0
        # ~ window_size = 8  
        # ~ window_end_i =  window_start_i+ window_size
        # ~ window_move_i = 4
        
        # ~ steps = 30
        # ~ for a in range( 1 , steps):
            # ~ allowed_configs = [] 
            # ~ allowed_configs_cost = [] 
            # ~ #look at all configs in this range, and record the cost
            # ~ bool_permut = list(itertools.product([True, False], repeat=window_size))#this make list of all boolean permutations 
            # ~ for bool_list in bool_permut:
                # ~ config = list(planting_best_bool)
                # ~ for a, val in enumerate( range(window_start_i, window_end_i)):
                    # ~ config[val] = bool_list[a]
               
                # ~ cost= self.cost_func(config)
                # ~ print( best_cost , cost)
                # ~ print( config[:20])
                # ~ if cost < best_cost:
                    # ~ best_cost = cost
                    # ~ planting_best_bool = list(config)
                    # ~ print("new best cost" , cost)
                    # ~ print(config)
            
            
            
            # ~ window_start_i += window_move_i
            # ~ window_end_i += window_move_i
            
            
        # ~ print( planting_best_bool)
            
        
    
    def optimize_cultivar( self , startdate , enddate ):
        self.startdate = startdate
        self.enddate = enddate
        
        
        bnds = [(-0.1, 0) ]*self.ndates
        guess_areas = np.zeros(self.ndates)
        s = self.sample_crop_plan.details['cultivar_class'].shelf_life_post_harvest
        for a, val in enumerate(guess_areas):
            if a%s == 0:
                guess_areas[a] = 1 
        
        integrality_bools = []
        for b in range(0 , len(bnds)):
            if self.yield_vec[b] == 0 and guess_areas[b] < 0 :
                bnds[b] = (-0,0)
                guess_areas[b] = 0
            elif guess_areas[b] > 0:
                bnds[b] = (-0.1, 1 )
                guess_areas[b] = 1
                
            integrality_bools.append(True)##all boolean optimization params
        
        nrand = 6    
        population = 10
        initial_population = np.zeros( (population, self.ndates) )
        for a in range( 0, population):
            initial_population[a,:] = guess_areas
            
        
        print(initial_population[a,:])
        
        
        
       
        for pcol in range(0,population):
            for a, val in enumerate(guess_areas):
                if a%s == 0:
                    r = random.uniform(0,1)
                    if r > 0.8:
                        initial_population[pcol,a] = random.randint( 0 , 1)
            
        ret = differential_evolution(self.cost_func, bnds, integrality = integrality_bools, popsize = population , init=  initial_population)
        
        
        minimizer_kwargs = {"method": "BFGS"}
        # ~ ret = basinhopping(self.cost_func, guess_areas, minimizer_kwargs=minimizer_kwargs,niter=2)
        #ret = minimize(self.cost_func, guess_areas, method='Nelder-Mead',bounds=bnds, tol=1e-6)
        
        print(ret.x)
        print(self.cost_func(ret.x) , " = cost best")
        print(ret.x)
        ret.x = ret.x * (ret.x >= 0)
        
        #clean optimizer results: 
        
        self.optimum_planting_areas = self.find_planting_areas(  ret.x , self.allowed_harvest_dates)
        return area_vector

'''
# ~ class optimizer:
    # ~ def __init__(self , fd , cultivar, sample_crop_plan):
        # ~ self.cultivar= cultivar
        # ~ self.farm_data = fd
        # ~ self.yield_vec = [1 ,1] #how much yield in kg from a crop planted on day this index represents as in self.dates
        # ~ self.demand_kg_per_day = [ 1 , 1]
        self.yield_kg_per_day = [ 0 , 0]
        # ~ self.dates = [ datetime(1901,1,1) , datetime(1901,1,2) ]
        # ~ self.optimum_planting_areas = [ 1.4 , 1]
        # ~ self.sales = [ 1 , 1] #how much we can sell each day. never higher than demand
        # ~ self.ndates = len(self.dates)
        # ~ self.demand = [ 1 , 1]#this is demand in kg per day for each of the self.dates  
        # ~ self.demand_forcing_intensity = 0.1
        # ~ self.labour_constant_min = 10
        # ~ self.labour_min_per_m2 = 60
        # ~ self.startdate = datetime(1901,1,1)
        # ~ self.enddate = datetime(1901,1,1)
        # ~ self.sample_crop_plan = sample_crop_plan
        # ~ self.H = np.zeros([2,2]) #yield or harvest matrix
        
    
    # ~ def make_yield_matrix(self):
        # ~ #populate self.dates
        # ~ self.dates = pd.date_range(start= self.startdate, end=self.enddate  , freq='D').to_list()
        # ~ self.ndates = len(self.dates)
        
        # ~ #sim all these dates if the temperature makes sense:
        # ~ list_of_sim_dfs = [pd.DataFrame()]* self.ndates
        # ~ print(self.farm_data.weather.df_predict)
        
        # ~ print(self.farm_data.weather.df_predict.loc[ datetime(2024,3,15) : datetime(2024,3,30) ] )

        
        # ~ for i, dt in enumerate(self.dates):
            # ~ #is it too cold to plant? 
            # ~ min_temp = ( self.farm_data.weather.df_predict['Tmin(C)'].loc[dt])
            # ~ print(min_temp , "min temp")
            # ~ if min_temp <= self.cultivar.death_temperature:
                # ~ pass
            # ~ else:
                # ~ list_of_sim_dfs[i] = aquacrop_wrapper.simAquaCrop(  'plansim', "./aquacrop" , dt , self.farm_data.weather.df_predict['datetime'].iloc[-2] ,  self.farm_data.weather.df_predict , self.cultivar.minimum_harvest_temperature, self.cultivar.cropfilename , self.sample_crop_plan.details['irrigation.IRR']) 

        # ~ #ok, now go through those sims and pick out the yield:
        
        # ~ yieldF = np.zeros(self.ndates) # the yieldF[i] is yeild for crop planted on date index i 
        # ~ harvest_dates = [datetime(1901,1,1)]*self.ndates
        # ~ harvest_date_index = np.zeros(self.ndates)
        # ~ print(yieldF)

        # ~ for i, dt in enumerate(self.dates):
            # ~ yieldF[i] = 0 
            # ~ if( len(list_of_sim_dfs[i].index)>=1): 
                # ~ yieldF[i] = list_of_sim_dfs[i]['Y(fresh)'].iloc[-1]*1000/10000 #this units thing is so we get kg/m2 not ton per hectacre
                
                # ~ harvest_dates[i] = list_of_sim_dfs[i]['dateobject'].iloc[-1]
                # ~ try: 
                    # ~ harvest_date_index[i] = int(self.dates.index(harvest_dates[i]))
                    print(type(harvest_date_index[i]))
                # ~ except: 
                    # ~ #didn't have that date in our list, it's probably too far in the future to consider , so just put 0, that will ignore this yeild  
                    # ~ harvest_date_index[i] = 0
        # ~ print(harvest_date_index)
        
        # ~ #for matrix M[b,a]= Y , Y is kg produce, b is harvest date, a is planting date 
        # ~ self.H = np.zeros([self.ndates , self.ndates])
        # ~ self.yield_vec = yieldF
        # ~ for i, y in enumerate(yieldF):
            # ~ b = int(harvest_date_index[i])
            # ~ a = i 
            # ~ if( b != 0 and b <self.ndates):
                # ~ self.H[ b, a] = y
                
        # ~ print(self.H)
        
        
    
    # ~ def estimate_labour_for_crop(self  ):
        # ~ crop_plan = self.sample_crop_plan
        # ~ #give a constan time for this crop, and a time per m2 
        
        
        # ~ #if there are events in past crop plans with the same description, worker id as the proposed ones,
        # ~ #make a list of mean_past_events where each event has a mean time scaled by area
        # ~ if ( len(self.farm_data.past_crop_plan_list) > 0 ): 
            # ~ self.farm_data.mean_past_events = [ self.past_crop_plan_list[0].event_list[0] ]
            # ~ for past_crop_plan in self.farm_data.past_crop_plan_list:
                # ~ for pe in past_crop_plan:
                # ~ #check if pe is in mean_past_events. 
                    # ~ for me in mean_past_events:
                        # ~ if pe.compare_events(me) == True:
                            # ~ #update the mean, add the area aka soil plot ids and add and time_taken_min
                            # ~ me.details['time_taken_min'] = me.details['time_taken_min'] + pe.details['time_taken_min'] 
                            # ~ me.details['soil_plot_ids'] = me.details['soil_plot_ids']  + pe.details['soil_plot_ids'] 
                        # ~ else:
                            # ~ mean_past_events.append(pe)

        # ~ #now look at the proposed events. crop_plan.event_list
        
        # ~ #now make a best time 'time_estimate_generated' for each of these events using either mean_past_events or calcualtion from human input
        print( len(joined_proposed_events) ) 
        joined_proposed_events[0].pretty_print() 
        
        # ~ area_time_min = 0
        # ~ constant_time_min = 0 
        # ~ switching_min = 2 #time cost to switch jobs  
        # ~ for e in crop_plan.event_list:
            # ~ area = 0 
            # ~ for sid in e.details['soil_plot_ids']:
                # ~ area+= self.soil_plot_dict[ sid ].details['area_m2']
        
            # ~ e.details['time_estimate_generated']= switching_min + e.details['time_estimate_min_per_m2']*area
            # ~ area_time_min += e.details['time_estimate_min_per_m2']
            # ~ constant_time_min += switching_min
        
        # ~ self.labour_constant_min = constant_time_min
        # ~ self.labour_min_per_m2 = area_time_min
        
        # ~ return  constant_time_min, area_time_min
        
    # ~ def estimate_labour_for_crop_Matrix(self , area_vector  ):
        # ~ #give a time for this crop area vector 
        # ~ labour_time = 0
        # ~ for a in area_vector:
            # ~ if a > 0:
                # ~ labour_time += a*self.labour_min_per_m2 + self.labour_constant_min
        
        # ~ return labour_time
        
    # ~ def set_constant_demand(self , kg_per_day):
        # ~ self.demand = np.ones(self.ndates)*kg_per_day
        
    # ~ def estimate_sales( self, harvest_vec):
        # ~ self.sales = np.zeros(self.ndates)
        # ~ #every day you potentially harvest some crop, and you sell some crop
        # ~ #you need to know how long you can hold the crop after harvesting. That's information in cultivar
        # ~ shelf_life = self.sample_crop_plan.details['cultivar_class'].shelf_life_post_harvest
        
        # ~ #so walk though the list with a deque of how much crop and how old it is in storage
        # ~ stock = collections.deque(maxlen=shelf_life)
        # ~ total_sold = 0 
        # ~ for i in range(0 , self.ndates ):
            # ~ today_demand = self.demand[i] 
            # ~ stock.append(harvest_vec[i])#add today's harvest, if there is any old harvest it gets dumped
            print("stock" , stock)
            # ~ for a, val in enumerate(stock):
                print("a" , a )
                # ~ if stock[a] >= today_demand:
                    # ~ sold =  today_demand
                    # ~ today_demand = today_demand - sold
                    # ~ stock[a] = stock[a] - sold
                    # ~ total_sold += sold
                    # ~ self.sales[i] += sold

                # ~ if stock[a] < today_demand:
                    # ~ sold =  stock[a]
                    # ~ today_demand = today_demand - sold
                    # ~ stock[a] = stock[a] - sold
                    # ~ total_sold += sold
                    # ~ self.sales[i] += sold
        
        # ~ return total_sold
        
        
        
    # ~ def cost_func( self, area_vector):
        # ~ area_vector = area_vector * (area_vector >= 0) #this sets all the negative areas to zero
        # ~ yield_vec = self.H.dot(area_vector)
        # ~ sold = self.estimate_sales( yield_vec) 
        # ~ time_labour = self.estimate_labour_for_crop_Matrix( area_vector) 
        # ~ print(-sold/time_labour , sold , time_labour )
        # ~ return -sold/time_labour #this kg sold/min of labour, obviously this needs to be maximized, use negative to minimize it
    
    # ~ def optimize_cultivar( self , startdate , enddate ):
        # ~ self.startdate = startdate
        # ~ self.enddate = enddate
        
        
        # ~ bnds = [(-0.1, None) ]*self.ndates
        # ~ guess_areas = np.zeros(self.ndates)
        # ~ s = self.sample_crop_plan.details['cultivar_class'].shelf_life_post_harvest
        # ~ for a, val in enumerate(guess_areas):
            # ~ if a%s == 0:
                # ~ guess_areas[a] = 1 
        
        # ~ integrality_bools = []
        # ~ for b in range(0 , len(bnds)):
            # ~ if self.yield_vec[b] == 0:
                # ~ bnds[b] = (-0,0)
            # ~ else:
                # ~ bnds[b] = (-0.1, 1 )
                
            # ~ integrality_bools.append(True)##all boolean optimization params
        
        
        # ~ optimal_planting = differential_evolution(self.cost_func, bnds, integrality = integrality_bools )
        
        # ~ print(optimal_planting.x)
        # ~ optimal_planting.x = optimal_planting.x * (optimal_planting.x >= 0)
        
        # ~ #clean optimizer results: 
        
        # ~ self.optimum_planting_areas = self.find_planting_areas(  optimal_planting.x , self.allowed_harvest_bool)
        # ~ return area_vector
        
        


        
    '''
    
