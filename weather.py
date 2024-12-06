import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np


class weather:
    def __init__(self):
        self.last_observed_time = 0 #this is timestamp for the last actual data we have, after that it's all prediction
        self.df_daily = pd.DataFrame() #this is observed and forcast weather all in a lump so we can run the crop model 
        self.df_observed = pd.DataFrame() #real weather as observed
        #weather df format:[ 'Day', 'Month' , 'Year' , 'Tmin(C)' , 'Tmax(C)' , 'Prcp(mm)' , 'ET0']
        self.df_predict = pd.DataFrame()
        
    def load_observed_weather(self):
        self.df_observed = pd.read_csv('./localWeatherData/climate_ofp.csv') 
        self.df_observed['Datetime'] = pd.to_datetime(self.df_observed['Datetime'])
        self.df_observed = self.df_observed.set_index('Datetime') 
        
    def fill_with_prediction( self, ndays, static):
        #look at the observed weather and guess at the future weather
        last_datetime = datetime.fromtimestamp( self.last_observed_time)
        self.df_observed = self.df_observed.loc[:last_datetime]
        
        print(self.df_observed)

       
        
        #make a range of dates into the future 
        datelist = pd.date_range(last_datetime, periods=ndays)
        print(datelist)
        
        listdeltas= []
        for a in range( 1 , 11):
            listdeltas.append( pd.Timedelta(days=a*365) )
            
        yb =random.randint(0, len(listdeltas)-1 )
        print(yb,len(listdeltas))
        if static == True:
            yb = 2
        
        
        df = pd.DataFrame(columns=self.df_observed.columns.values, index=datelist)
        
        for d in datelist:
            Tmin = []
            Tmax = []
            ET0 = []
            prcp =[]
            #look at the past 10 years on this date: 
            #make a list of the rows we get: 
            rowlist = []
            for bdelta in listdeltas:
                
                ET0.append (self.df_observed['ET0'].loc[d - bdelta])
                prcp.append (self.df_observed['Prcp(mm)'].loc[d - bdelta])
                Tmax.append (self.df_observed['Tmax(C)'].loc[d - bdelta])
                Tmin.append (self.df_observed['Tmin(C)'].loc[d - bdelta])
            # ~ Datetime,Day,Month,Year,Tmin(C),Tmax(C),Prcp(mm),ET0
            
            df.loc[d] = pd.Series({'Day':d.day, 'Month':d.month, 'Year':d.year, 'Tmin(C)':Tmin[yb] , 'Tmax(C)':Tmax[yb], 'Prcp(mm)':prcp[yb] , 'ET0':ET0[yb] })
            
            # ~ print(np.mean(ET0))
    
        dfout = pd.concat( [self.df_observed, df])
        print(dfout)
        idstr = str(self.df_observed.index[-1].day) + '-' +str(self.df_observed.index[-1].month) + '-' + str(self.df_observed.index[-1].year)
        dfout.to_csv('predicted_' + idstr+ '_climate_ofp.csv')
        dfout['datetime'] = pd.to_datetime(dfout[['Year', 'Month', 'Day']]) 
        dfout = dfout.set_index('datetime')
        dfout['datetime'] = dfout.index
        idx = np.unique( dfout.index.values, return_index = True )[1]
        dfout = dfout.iloc[idx]   


        dfout['Tmax(C)'] = pd.to_numeric(dfout['Tmax(C)'],errors = 'coerce')
        dfout['Tmin(C)'] = pd.to_numeric(dfout['Tmin(C)'],errors = 'coerce')
        dfout['Prcp(mm)'] = pd.to_numeric(dfout['Prcp(mm)'],errors = 'coerce')
        dfout['ET0'] = pd.to_numeric(dfout['ET0'],errors = 'coerce')
        
        dfout['Day'] = pd.to_numeric(dfout['Day'],errors = 'coerce')
        dfout['Month'] = pd.to_numeric(dfout['Month'],errors = 'coerce')
        dfout['Year'] = pd.to_numeric(dfout['Year'],errors = 'coerce')
        
        self.df_predict = dfout

        # ~ print(dfout.info)
        # ~ print(self.df_predict.loc[ datetime(2024,3,15) : datetime(2024,3,30) ] )

        # ~ quit()
