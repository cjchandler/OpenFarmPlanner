# load daily data from solcast

#walk through all my files with name *past_7_days.py

import os, glob
import pandas as pd
import dateutil.parser
import numpy as np
from datetime import datetime, date, time
from datetime import timedelta
from eto import ETo, datasets



def save_unified_df_of_solcast_past7day_files( folder_path ) :

    # ~ folder_path = '/home/carl/Git_Projects/datalogging/solcast'
    # ~ folder_path = '../../datalogging/solcast'
    dfall = pd.DataFrame()
    dflist = []
    for filename in glob.glob(os.path.join(folder_path, '*past7days.csv')):
      df = pd.read_csv(  filename, names = ['ghi'	,'ebh',	'dni'	,'dhi'	,'cloud_opacity'	,'period_end',	'period'], header = None)

      dflist.append(df)
      

    dfall = pd.concat(dflist)
    df = dfall.drop_duplicates()
    #look at all the period_end entries. make a mask of good ones that are strings
    good_indexes = np.zeros( len(df.index))
    for idx, i in enumerate(df.index):
        if isinstance( df['period_end'].loc[i] , str ): #it is a string
            if( df[period_end].loc[i].isdigit() == True): #it has a number in it
                good_indexes[idx] = True #probably a good date
            else:
                good_indexes[idx] = False
        else:
            good_indexes[idx] = False

    df = df.drop( good_indexes)

    df[['ghi'	,'ebh',	'dni'	,'dhi'	,'cloud_opacity']] = df[['ghi'	,'ebh',	'dni'	,'dhi'	,'cloud_opacity']].apply(pd.to_numeric)

    #make a date time column
    time_period_end = df["period_end"].to_list()
    print(time_period_end)

    date_list = []
    for a in range(0, len(time_period_end)):
        print(time_period_end[a])
        temp_data_sun = dateutil.parser.parse(time_period_end[a])
        
        timestamp = datetime.timestamp(temp_data_sun)
        dt_object = datetime.fromtimestamp(timestamp)

        datetimeunaware = dt_object

        date_list.append(dt_object)

    df["datetime"] = date_list

    df = df.set_index('datetime') 
    df= df.sort_index()
    df = df.interpolate()



    print(df)
    df.to_csv("daily_solcast_joined.csv")
    
# ~ save_unified_df_of_solcast_past7day_files('/home/carl/Git_Projects/datalogging/solcast')

# ~ df = pd.read_csv("daily_solcast_joined.csv")
#join this with daily historical weather 
# ~ df_yar = pd.read_csv("yarA_27nov2024.csv")


daily_files = [ "yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]

def load_daily_old_data( filelist  ):
        df_yar = pd.DataFrame()
        dfwater = pd.DataFrame()
        for a in filelist: #["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]:
            path = "./"
            filestring = a 
            dfwater = pd.read_csv(path + filestring, sep=',')
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
        
        dfclimate= pd.DataFrame()
        dfclimate['Tmin(C)'] = df_yar['MIN_TEMPERATURE']
        dfclimate['Tmax(C)'] = df_yar['MAX_TEMPERATURE']
        dfclimate['Prcp(mm)'] = df_yar['TOTAL_PRECIPITATION']
        dfclimate['Day'] = df_yar['LOCAL_DAY'] 
        dfclimate['Month'] = df_yar['LOCAL_MONTH'] 
        dfclimate['Year'] = df_yar['LOCAL_YEAR'] 
        
        return dfclimate

new_daily_files = ["yarA_2024.csv"]
def load_daily_new_data( filelist  ):
        df_yar = pd.DataFrame()
        for a in filelist: #["yarA0.csv", "yarA1.csv","yarA2.csv","yarA3.csv","yarA4.csv" ]:
            path = "./"
            filestring = a 
            dfwater = pd.read_csv(path + filestring, sep=',')
            print(a)

            dfwater['Datetime'] = pd.to_datetime(dfwater['Date/Time'])
            # ~ print(dfwater)

            dfwater['Datetime'] = dfwater['Datetime']
           

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

def load_all_daily_historical( newlist , oldlist): 
    df1 = load_daily_new_data(newlist)
    df2 = load_daily_old_data(oldlist) 
    
    df = pd.concat([ df1, df2])
    
    df['tempdatetime'] = df.index
    df = df.drop_duplicates(subset=['tempdatetime'])
    df = df.drop('tempdatetime', axis=1)
    df = df.sort_index()
    df = df.interpolate()
    df = df.dropna()
    return df
    
dfclimate = load_all_daily_historical(new_daily_files,daily_files)
print(dfclimate)
    




def load_30_min_solcast( filename ): #assumes UTC times 
        dfsolcast = pd.read_csv(filename)
        dfsolcast['Datetime'] = pd.to_datetime(dfsolcast['datetime'])
        dfsolcast = dfsolcast.set_index('Datetime')

        df = pd.DataFrame()
        df['R_s joules per hour'] = dfsolcast['ghi']*60*30
        df['R_s'] = df['R_s joules per hour']/(1000000.)
       
        dfsum = df.resample('D').sum()
        
        dfsum.drop(dfsum.tail(1).index,inplace=True)#drop the first and last because daily sum might be only doing half a day
        dfsum.drop(dfsum.head(1).index,inplace=True)
        
        return dfsum 

def load_60_min_solcast(filename):
        df = pd.read_csv( filename ,  sep=',')
    
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
        
        dfa = pd.DataFrame()
        dfa['R_s joules per hour'] = df['Ghi']*60*60
        dfa['R_s'] = dfa['R_s joules per hour']/(1000000.)
       
        dfsum = dfa.resample('D').sum()
        return dfsum
        
def load_all_daily_solcast_R_s( file30min , file60min):
    df1 = load_30_min_solcast(file30min)
    df2 = load_60_min_solcast(file60min)
    
    df = pd.concat([ df1, df2])
    
    df['tempdatetime'] = df.index
    df = df.drop_duplicates(subset=['tempdatetime'])
    df = df.drop('tempdatetime', axis=1)
    df = df.drop('R_s joules per hour', axis=1)
    df = df.sort_index()
    df = df.interpolate()
    df = df.dropna()
    
    print(df)
    return df
    
    
        
solcast_60min_file = "43.913601_-66.070782_Solcast_PT60M.csv" 
solcast_30min_file = "daily_solcast_joined.csv"
df_sun = load_all_daily_solcast_R_s( solcast_30min_file, solcast_60min_file) 
lat = 43.6
lon = -66

def do_ET0( dfclimate , df_sun, lat ,lon ): 
    dfall = pd.concat([dfclimate , df_sun], axis=1)
    
    df = pd.DataFrame()
    df['T_min'] = dfall['Tmin(C)']
    df['T_max'] = dfall['Tmax(C)']

    df['R_s'] = dfall['R_s']
    
    print(df.tail(40))
    
    #split into 2 dfs one for sun data, one without
    dftempsun = df[df['R_s'] > 0.0 ]
    dftempsun = dftempsun.interpolate()

    dftemp1 = df[df['R_s'] == 0.0 ] #is R_s is zero, that probably means no data not that the sun didn't shine all day
    mask = pd.notna(df['R_s'])

    dftemp2 = df[ np.invert(mask) ] #so this is then a mask of only nans
    # ~ print(dftemp2)
  
    dftemponly = pd.concat( [ dftemp1 , dftemp2])
    
    et1 = ETo()

    z_msl = 70

    TZ_lon = 0
    freq = 'D'
    # ~ print(dftempsun)
    # ~ dftempsun.to_csv("dummy1.csv")
    # ~ dftemponly.to_csv("dummy2.csv")
    et1.param_est(dftempsun, freq, z_msl, lat, lon, TZ_lon)
    dftempsun['ET0'] = et1.eto_fao()

    et1.param_est(dftemponly, freq, z_msl, lat, lon, TZ_lon)
    dftemponly['ET0'] = et1.eto_fao()
    
    dfeto = pd.concat( [ dftemponly , dftempsun])
    dfeto = dfeto.sort_index()
    
    dfclimate['ET0'] = dfeto['ET0']
    
    
    
    return dfclimate

dfclimate = do_ET0( dfclimate , df_sun , lat , lon)
print(dfclimate)
dfclimate.to_csv("dummy3.csv")
