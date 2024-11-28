#this is a script to read solcast historical data and canad historical daily data into our Openfarmplanner data format


from itertools import islice
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date, time
from datetime import timedelta
import matplotlib.dates as mdates
from pytz import timezone
import pytz
import numpy as np
import dateutil.parser
from eto import ETo, datasets
import os

class climate:
    def __init__(self):
        self.data_path  = "" 
        self.solcast_filename = ""
        self.list_historical_daily_files = []
        self.lon = 0 
        self.lat = 0 
        
        
        self.df_solcast_all = pd.DataFrame()
        self.df_historical = pd.DataFrame()
        
    def load_solcast_all(self):
        df = pd.read_csv(self.data_path + self.solcast_filename, sep=',')
    
        #make a date time column
        time_period_end = df["PeriodEnd"] 
        date_list = []
        for a in range(0, len(time_period_end)):
            temp_data_sun = dateutil.parser.isoparse(time_period_end[a])
            
            timestamp = datetime.timestamp(temp_data_sun)
            dt_object = datetime.fromtimestamp(timestamp)

            datetimeunaware = dt_object

            date_list.append(dt_object)

        df["datetime"] = date_list

        df = df.set_index('datetime') 

        self.df_solcast_all = df 
    






    def reformat_solcast_to_daily_add_ET0( self ): #assumes UTC times 
        df = pd.DataFrame()
        df['T_mean'] = self.df_solcast_all['AirTemp']
        df['R_s joules per hour'] = self.df_solcast_all['Ghi']*60*60
        df['R_s'] = df['R_s joules per hour']/(1000000.)
        df['RH_mean'] = self.df_solcast_all['RelativeHumidity']
        df['U_z'] = self.df_solcast_all['WindSpeed10m']
        df['P']= self.df_solcast_all['SurfacePressure']

        dfmean = df.copy()
        
        dfmaxD = df.resample('D').max()
        dfminD = df.resample('D').min()
        
        dfminmax = pd.DataFrame()
        dfminmax.index = dfmaxD.index
        dfminmax['Tmax(C)'] = dfmaxD['T_mean']
        dfminmax['Tmin(C)'] = dfminD['T_mean']
        
        et1 = ETo()

        z_msl = 70
        # ~ lat = 43.6
        # ~ lon = -66
        TZ_lon = 0
        freq = 'H'
        et1.param_est(df, freq, z_msl, self.lat, self.lon, TZ_lon)

        # ~ print(et1.ts_param.head())
        df['ET0'] = et1.eto_fao()
        dfsumD = df.resample('D').sum()
        
        dfminmax['ET0'] = dfsumD['ET0']
        # ~ dfminmax.plot()
        # ~ plt.show()
        # ~ quit()
        self.df_solcast_all = dfminmax




    def load_daily_data( self  ):
        df_yar = pd.DataFrame()
        for a in self.list_historical_daily_files: #["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]:
            # ~ path = "/home/carl/Git_Projects/AquaCropFAO/yarmouthData/"
            filestring = a 
            dfwater = pd.read_csv(self.data_path + filestring, sep=',')
            print(a)

            dfwater['Datetime'] = pd.to_datetime(dfwater['LOCAL_DATE'])
            # ~ print(dfwater)

            dfwater['Datetime'] = dfwater['Datetime']
           

            df_yar = pd.concat([df_yar , dfwater])
            
        df_yar = df_yar.drop_duplicates(subset=['Datetime'])
        df_yar = df_yar.set_index('Datetime')
        df_yar.tz_localize('UTC')
        df_yar = df_yar.sort_index()
        df_yar = df_yar.interpolate()
        # ~ start = datetime(y, 1, 1, 0, 0, 0, 0) 
        # ~ end = datetime(y+2, 1, 1, 0, 0, 0, 0) 
        df_out = pd.DataFrame()
        self.df_historical = df_yar  #.loc[start:end]
        
        # ~ print(self.df_historical.columns)

     

    def get_daily_data_for_year_no_solcast(self, year_start , year_end ) :
        start = datetime(year_start, 1, 1, 0, 0, 0, 0) 
        end = datetime(year_end+1, 1, 1, 0, 0, 0, 0) 
        
        dfwater = pd.DataFrame()
        dfwater = self.df_historical.loc[start:end]
        
        df = pd.DataFrame()
        
        df['Tmin(C)'] = dfwater['MIN_TEMPERATURE']
        df['Tmax(C)'] = dfwater['MAX_TEMPERATURE']
        df['Prcp(mm)'] = dfwater['TOTAL_PRECIPITATION']
        df['Day'] = dfwater['LOCAL_DAY']
        df['Month'] = dfwater['LOCAL_MONTH']
        df['Year'] = dfwater['LOCAL_YEAR']
        
        dfeto = pd.DataFrame()
        dfeto['T_mean'] = dfwater['MEAN_TEMPERATURE']
        dfeto['T_min'] = dfwater['MIN_TEMPERATURE']
        dfeto['T_max'] = dfwater['MAX_TEMPERATURE']
        
        
        et1 = ETo()

        z_msl = 70
        # ~ lat = 43.6
        # ~ lon = -66
        TZ_lon = 0
        freq = 'D'
        et1.param_est(dfeto, freq, z_msl, self.lat, self.lon, TZ_lon)

        # ~ print(et1.ts_param.head())
        df['ET0'] = et1.eto_fao()
        df = df[['Day', 'Month' , 'Year' , 'Tmin(C)' , 'Tmax(C)' , 'Prcp(mm)' , 'ET0' ]]

        print(df)
        

    def get_daily_data_for_year(self, year_start , year_end ) :
    
        start = datetime(year_start, 1, 1, 0, 0, 0, 0) 
        end = datetime(year_end+1, 1, 1, 0, 0, 0, 0) 
        dfeto = pd.DataFrame()
        dfeto = self.df_solcast_all.loc[start :end]
        dfwater = pd.DataFrame()
        dfwater = self.df_historical.loc[start:end]
            
        

        df = pd.DataFrame()
        df['ET0'] = dfeto['ET0']
        df['Tmin(C)'] = dfwater['MIN_TEMPERATURE']
        df['Tmax(C)'] = dfwater['MAX_TEMPERATURE']
        df['Prcp(mm)'] = dfwater['TOTAL_PRECIPITATION']
        df['Day'] = pd.DatetimeIndex(df.index).day
        df['Month'] = pd.DatetimeIndex(df.index).month
        df['Year'] = pd.DatetimeIndex(df.index).year
        df = df[['Day', 'Month' , 'Year' , 'Tmin(C)' , 'Tmax(C)' , 'Prcp(mm)' , 'ET0' ]]

        df = df.interpolate()

        # ~ print(dfwater)
        #df.to_csv("climate_ofp.csv")
        
        # ~ df.plot()
        # ~ plt.show()
        # ~ quit()
        
        
        return df
        
c = climate()
c.list_historical_daily_files = ["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]
c.solcast_filename = "43.913601_-66.070782_Solcast_PT60M.csv" 
c.data_path= "./"
c.lon = -66
c.lat = 43.9
c.load_solcast_all()
c.reformat_solcast_to_daily_add_ET0()
c.load_daily_data()
c.get_daily_data_for_year_no_solcast(2007, 2008)
dftemp = c.get_daily_data_for_year(2007 , 2008)
print(dftemp)
#dftemp.to_csv("climate_ofp.csv")
