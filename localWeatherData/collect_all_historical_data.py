# load daily data from solcast

#walk through all my files with name *past_7_days.py

import os, glob
import pandas as pd
import dateutil.parser
import numpy as np
from datetime import datetime, date, time
from datetime import timedelta
from eto import ETo, datasets



class weather_data_loader: 
    def __init__(self):
        self.dfclimate = pd.DataFrame() #this is the output 
        self.path_to_7day_solcast = "/home/carl/Git_Projects/datalogging/solcast"
        self.filepath_60_min_solcast = "./43.913601_-66.070782_Solcast_PT60M.csv"
        self.climate_change_canada_filelist = [ "yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]
        self.climate_weather_gc_filelist = ["yarA_2024.csv"]
        
        
        self.df_30_min_solcast = pd.DataFrame()
        self.df_R_s = pd.DataFrame()
        
        self.lat = 43.6
        self.lon = -66   
        
        
    def add_datetime_to_df(self , df , date_like_col ):
         #make a date time column
        time_period_end = df[date_like_col].to_list()
        print(time_period_end)

        date_list = []
        for a in range(0, len(time_period_end)):
            temp_data_sun = dateutil.parser.parse(time_period_end[a])
        
            #This gets rid of the timezone aware issues. 
            timestamp = datetime.timestamp(temp_data_sun)
            dt_object = datetime.fromtimestamp(timestamp)

            # ~ datetimeunaware = dt_object

            date_list.append(dt_object)

        df["datetime"] = date_list

        df = df.set_index('datetime') 
        df= df.sort_index()
        
        return df
        
        
        
    def load_7day_solcast(self): ##this is really slow on my computer, but runs infrequently so no big deal I hope
        # ~ folder_path = '/home/carl/Git_Projects/datalogging/solcast'
        # ~ folder_path = '../../datalogging/solcast'
        dfall = pd.DataFrame()
        dflist = []
        #look at all the files with the right ending. 
        #The names of the col has changed over the years, but the order is the same, so I add my own col names
        for filename in glob.glob(os.path.join(self.path_to_7day_solcast, '*past7days.csv')):
          df = pd.read_csv(  filename, names = ['ghi'	,'ebh',	'dni'	,'dhi'	,'cloud_opacity'	,'period_end',	'period'], header = None)

          dflist.append(df)
          

        dfall = pd.concat(dflist)
        df = dfall.drop_duplicates()
        
        #look at all the period_end entries. make a mask of good ones that are strings
        #some are bad, don't know why exactly 
        good_indexes = np.zeros( len(df.index))
        for idx, i in enumerate(df.index):
            if isinstance( df['period_end'].loc[i] , str ): #it is a string
                if( df[period_end].loc[i].isdigit() == True): #it has a number in it
                    good_indexes[idx] = True #probably a good date
                else:
                    good_indexes[idx] = False
            else:
                good_indexes[idx] = False

        df = df.drop( good_indexes)#this drops the false ones

        #make sure the data is numeric
        df[['ghi'	,'ebh',	'dni'	,'dhi'	,'cloud_opacity']] = df[['ghi'	,'ebh',	'dni'	,'dhi'	,'cloud_opacity']].apply(pd.to_numeric)

        df = self.add_datetime_to_df( df , 'period_end')
        
        df = df.interpolate()



        self.df_30_min_solcast = df 
        # ~ df.to_csv("daily_solcast_joined.csv")
        
    def convert_30_min_solcast_to_R_s( self ): #assumes UTC times 
        self.load_7day_solcast()
        dfsolcast = self.df_30_min_solcast
        print(dfsolcast)
        # ~ dfsolcast['Datetime'] = pd.to_datetime(dfsolcast['datetime'])
        # ~ dfsolcast = dfsolcast.set_index('Datetime')

        df = pd.DataFrame()
        df['R_s joules per hour'] = dfsolcast['ghi']*60*30
        df['R_s'] = df['R_s joules per hour']/(1000000.)
       
        dfsum = df.resample('D').sum()
        
        dfsum.drop(dfsum.tail(1).index,inplace=True)#drop the first and last because daily sum might be only doing half a day
        dfsum.drop(dfsum.head(1).index,inplace=True)
        
        return dfsum 

    def convert_60_min_solcast_to_R_s(self):
        df = pd.read_csv( self.filepath_60_min_solcast ,  sep=',')
    
        #make a date time column
     
        df = self.add_datetime_to_df(df , "PeriodEnd")
        
        dfa = pd.DataFrame()
        dfa['R_s joules per hour'] = df['Ghi']*60*60
        dfa['R_s'] = dfa['R_s joules per hour']/(1000000.)
       
        dfsum = dfa.resample('D').sum()
        return dfsum
    
    def load_all_daily_solcast_R_s( self):
        df2 = self.convert_60_min_solcast_to_R_s()
        df1 = self.convert_30_min_solcast_to_R_s()
        
        df = pd.concat([ df1, df2])
        
        df['tempdatetime'] = df.index
        df = df.drop_duplicates(subset=['tempdatetime'])
        df = df.drop('tempdatetime', axis=1)
        df = df.drop('R_s joules per hour', axis=1)
        df = df.sort_index()
        df = df.interpolate()
        df = df.dropna()
        
        print(df)
        self.df_R_s = df
        return df
        

    def load_daily_climate_change_canada( self  ):
        #I got these file from https://climate-change.canada.ca/climate-data/#/daily-climate-data
        #lots of data, but not always including data from today, like 3 -4 days behind
        df_yar = pd.DataFrame()
        dfwater = pd.DataFrame()
        for a in self.climate_change_canada_filelist: #["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]:
            path = "./"
            filestring = a 
            dfwater = pd.read_csv(path + filestring, sep=',')
            print(a)

            dfwater['Datetime'] = pd.to_datetime(dfwater['LOCAL_DATE'])
            df_yar = pd.concat([df_yar , dfwater])
            
        df_yar = df_yar.drop_duplicates(subset=['Datetime'])
        df_yar = df_yar.set_index('Datetime')
        df_yar.tz_localize('UTC')
        df_yar = df_yar.sort_index()
        df_yar = df_yar.interpolate()
        
        dfclimate= pd.DataFrame()
        dfclimate['Tmin(C)'] = df_yar['MIN_TEMPERATURE']
        dfclimate['Tmax(C)'] = df_yar['MAX_TEMPERATURE']
        dfclimate['Prcp(mm)'] = df_yar['TOTAL_PRECIPITATION']
        dfclimate['Day'] = df_yar['LOCAL_DAY'] 
        dfclimate['Month'] = df_yar['LOCAL_MONTH'] 
        dfclimate['Year'] = df_yar['LOCAL_YEAR'] 
        
        return dfclimate


    def load_daily_climate_weather_gc( self  ):
        #I got these from https://climate.weather.gc.ca/historical_data/search_historic_data_e.html
        #only seem to have one year in each file
        df_yar = pd.DataFrame()
        for a in self.climate_weather_gc_filelist: #["yarA_2024.csv" ]:
            path = "./"
            filestring = a 
            dfwater = pd.read_csv(path + filestring, sep=',')
            print(a)
            dfwater['Datetime'] = pd.to_datetime(dfwater['Date/Time'])
            df_yar = pd.concat([df_yar , dfwater])
            
        df_yar = df_yar.drop_duplicates(subset=['Datetime'])
        df_yar = df_yar.set_index('Datetime')
        df_yar.tz_localize('UTC')
        df_yar = df_yar.sort_index()
      
        # ~ df_yar = df_yar.interpolate()
        
        dfclimate = pd.DataFrame()
        dfclimate['Tmax(C)'] = df_yar['Max Temp (°C)'] 
        dfclimate['Tmin(C)'] = df_yar['Min Temp (°C)'] 
        dfclimate['Prcp(mm)'] = df_yar['Total Precip (mm)'] 
        dfclimate['Day'] = df_yar['Day'] 
        dfclimate['Month'] = df_yar['Month'] 
        dfclimate['Year'] = df_yar['Year'] 
        dfclimate = dfclimate.dropna()#drop rows that have nan because those are rows in the future typically 
        
        
        return dfclimate

    def load_all_daily_historical(  self): 
        df1 = self.load_daily_climate_weather_gc()
        df2 = self.load_daily_climate_change_canada() 
        
        df = pd.concat([ df1, df2])
        
        df['tempdatetime'] = df.index
        df = df.drop_duplicates(subset=['tempdatetime'])
        df = df.drop('tempdatetime', axis=1)
        df = df.sort_index()
        df = df.interpolate()
        df = df.dropna()
        return df
        
   


    def do_ET0( self  ): 
        df_sun = self.load_all_daily_solcast_R_s()
        dfclimate = self.load_all_daily_historical()
        dfall = pd.concat([dfclimate , df_sun], axis=1)
        
        df = pd.DataFrame()
        df['T_min'] = dfall['Tmin(C)']
        df['T_max'] = dfall['Tmax(C)']

        df['R_s'] = dfall['R_s']
        df = df.interpolate()
        print(df)
        et1 = ETo()
        z_msl = 70
        TZ_lon = 0
        freq = 'D'

        et1.param_est(df, freq, z_msl, self.lat, self.lon, TZ_lon)
        # ~ print( et1.eto_fao())
        
       
        
        dfclimate['ET0'] = et1.eto_fao()  
            
        dfclimate = dfclimate[['Day', 'Month' , 'Year' , 'Tmin(C)' , 'Tmax(C)' , 'Prcp(mm)' , 'ET0' ]]
        dfclimate.to_csv("climate_ofp.csv")   
        print(dfclimate)



W = weather_data_loader()
W.path_to_7day_solcast = '/home/carl/Git_Projects/datalogging/solcast'
W.do_ET0()

