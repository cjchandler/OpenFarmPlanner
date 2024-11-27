# load daily data from solcast

#walk through all my files with name *past_7_days.py

import os, glob
import pandas as pd
import dateutil.parser
import numpy as np
from datetime import datetime, date, time
from datetime import timedelta

folder_path = '/home/carl/Git_Projects/datalogging/solcast'
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
