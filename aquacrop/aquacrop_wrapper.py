#run aquacrop sim for planning purposes

import pandas as pd
from datetime import datetime, date, time
from datetime import timedelta
import numpy as np
import dateutil.parser
from eto import ETo, datasets
import os




def save_file( lines, filename):
    f = open(filename, "w")
    for l in lines:
        f.write(l)
        f.write("\n")
    f.close()

def convert_value_to_str_with_colon(number, p , d):
    pos_spaces = p
    decimal_spaces = d 
    
    strnum = str(number) 
    if '.' in strnum:
        num,dec = strnum.split(".") 
        #pad it. 
        n = len(num)
        d = len(dec)
        out = " "*(pos_spaces - n) + num + "." + dec + (decimal_spaces-d)*" " + ":"
        
    else:
        #pad it. 
        n = len(strnum)
        out = " "*(pos_spaces - n) + strnum + " " + decimal_spaces*" " + ":"
    
    
    return out
    
def days_since_1901_convert( y , m , d ):
    out = y - 1901 
    out = out*365.25
    month_days = [ 0 , 31  , 59.25 , 90.25 , 120.25 , 151.25 , 181.25 , 212.25 , 243.25 , 273.25 , 304.25 , 334.25 ]
    out = out + month_days[m-1]
    out = out + d 
    return int(out) 
    
def days_since_jan1_convert( y , m , d ):
    month_days = [ 0 , 31  , 59.25 , 90.25 , 120.25 , 151.25 , 181.25 , 212.25 , 243.25 , 273.25 , 304.25 , 334.25 ]
    out =  month_days[m-1]
    out = out + d 
    return int(out) 


def make_sim_setup_files( location_tag , path, sim_datetime_start ,sim_datetime_end ,df_aquain , crop_file, irrigation_file ):
    
    #location_tag: this is a naming convention for the files produced from the df_predict or *climate_ofp.csv file 
    #location_tag should have no special characters or spaces
    #path is path to drectory where the ./DATA dir is and where the aquacrop executable is found
    
    #aquacrop represents day as days since jan 1 1901, 

    sim_datetime_year_jan1  = datetime(sim_datetime_start.year, 1, 1, 0, 0, 0, 0)
    df_aquain = df_aquain.loc[sim_datetime_year_jan1:]
    
    
    year_s = sim_datetime_start.year
    month_s = sim_datetime_start.month
    day_s = sim_datetime_start.day
    year_e = sim_datetime_end.year
    month_e = sim_datetime_end.month
    day_e = sim_datetime_end.day
    start_day_in_days_since_1901 = days_since_1901_convert( year_s , month_s , day_s)
    sim_datetime_1901  = datetime(1901, 1, 1, 0, 0, 0, 0)
    deltastart = sim_datetime_start - sim_datetime_1901
    deltaend = sim_datetime_end - sim_datetime_1901
    sim_start_days_into_year = days_since_jan1_convert(sim_datetime_start.year, sim_datetime_start.month, sim_datetime_start.day) #number of days since jan 1 on the year in question
   


    #first file is a list of other files:
    l = [None]*6
    l[0]= location_tag
    l[1]= " 7.1   : AquaCrop Version (oct 2024)"
    l[2] = location_tag + ".Tnx"
    l[3]= location_tag + ".ETo"
    l[4] = location_tag + ".PLU"
    l[5] = "MaunaLoa.CO2"
 
 
    save_file( l , path+"/DATA/"+location_tag +".CLI")

    ##I need to make file for: daily high and low temps  .Tnx 
    l = [None]*7
    l[0] = location_tag+ " daily highs and lows temperature"
    l[1] = "     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)"
    l[2] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First day of record (1, 11 or 21 for 10-day or 1 for months)"
    l[3] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First month of record"
    l[4] = convert_value_to_str_with_colon( year_s , 6 , 1) + "First year of record (1901 if not linked to a specific year)"
    l[5] = "  Tmin (C)   TMax (C)"
    l[6]= "======================="

    for a in range( 0 , len(df_aquain.index)):
        l.append( str( df_aquain["Tmin(C)"].iloc[a] ) + " " + str(df_aquain["Tmax(C)"].iloc[a]) )


    save_file( l , path+"/DATA/" +location_tag+ ".Tnx")

    #I need to make file for ETo
    l = [None]*7
    l[0] = location_tag + " daily ETo"
    l[1] = "     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)"
    l[2] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First day of record (1, 11 or 21 for 10-day or 1 for months)"
    l[3] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First month of record"
    l[4] = convert_value_to_str_with_colon( year_s , 6 , 1) + "First year of record (1901 if not linked to a specific year)"
    l[5] = "  Average ETo (mm/day)"
    l[6]= "======================="

    for a in range( 0 , len(df_aquain.index)):
        l.append( str( df_aquain["ET0"].iloc[a] )  )
    save_file( l , path+"/DATA/" +location_tag+ ".ETo")


    #I need to make a file for rainfall
    l = [None]*7
    l[0] = location_tag+ " daily precipitation mm"
    l[1] = "     1  : Daily records (1=daily, 2=10-daily and 3=monthly data)"
    l[2] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First day of record (1, 11 or 21 for 10-day or 1 for months)"
    l[3] = convert_value_to_str_with_colon( 1 , 6 , 1) + "First month of record"
    l[4] = convert_value_to_str_with_colon( year_s , 6 , 1) + "First year of record (1901 if not linked to a specific year)"
    l[5] = "Total Rain mm"
    l[6]= "======================="

    for a in range( 0 , len(df_aquain.index)):
        l.append( str( df_aquain["Prcp(mm)"].iloc[a] )  )
    save_file( l , path+"/DATA/" +location_tag + ".PLU")


    #make a calendar file
    l = [None]*9
    l[0]= "Onset: " + str(year_s) + " " +str(month_s) + " " + str(day_s) 
    l[1] = convert_value_to_str_with_colon( 7.1 , 10 , 3) + " AquaCrop Version (August 2023)"
    l[2] = convert_value_to_str_with_colon( 0, 10 , 3)   + " The onset of the growing period is fixed on a specific date"
    l[3] = convert_value_to_str_with_colon( -9 , 10 , 3)   + " Day-number (1 ... 366) of the Start of the time window for the onset criterion: Not applicable"
    l[4] = convert_value_to_str_with_colon( -9 , 10 , 3)   + " Length (days) of the time window for the onset criterion: Not applicable"
    l[5] = convert_value_to_str_with_colon(  sim_start_days_into_year, 10 , 3)   + " Day-number (1 ... 366) for the onset of the growing period"
    l[6] = convert_value_to_str_with_colon(  -9, 10 , 3)   + " preset value for generation of the onset: Not applicable"
    l[7] = convert_value_to_str_with_colon(  -9, 10 , 3)   + " Number of successive days: Not applicable"
    l[8] = convert_value_to_str_with_colon(  -9, 10 , 3)   + " Number of occurrences: Not applicable"

    save_file( l , path+"/DATA/" +location_tag + ".CAL")


    ##take all that and make a PRM file 
    cropfile = crop_file
    irrigationfile = irrigation_file

    l =[None]*49
    l[0]=   location_tag
    l[1]=(  convert_value_to_str_with_colon(7.1, 7 , 8) + "AquaCrop Version (August 2023)")
    l[2] = convert_value_to_str_with_colon(1, 7 , 8) + "Year number of cultivation (Seeding/planting year)"

    l[3] =  convert_value_to_str_with_colon( days_since_1901_convert(year_s , month_s, day_s) , 7 , 8) + " First day of simulation period "
    l[4] =  convert_value_to_str_with_colon( days_since_1901_convert(year_e , month_e, day_e) , 7 , 8) + " Last day of simulation period "
    l[5] =  convert_value_to_str_with_colon( days_since_1901_convert(year_s , month_s, day_s) , 7 , 8) + " First day of cropping period "
    l[6] =  convert_value_to_str_with_colon( days_since_1901_convert(year_e , month_e, day_e) , 7 , 8) + " Last day of cropping period "


    project = location_tag

    l[7] = "-- 1. Climate (CLI) file"
    l[8] = "   "+location_tag+ ".CLI"
    l[9] = "   './DATA/'"

    l[10] = "   1.1 Temperature (Tnx or TMP) file"
    l[11] =     "   "+location_tag+ ".Tnx"
    l[12] = "   './DATA/'"

    l[13] = "   1.2 Reference ET (ETo) file"
    l[14] =      "   "+location_tag+ ".ETo"
    l[15] = "   './DATA/'"

    l[16] = "   1.3 Rain (PLU) file"
    l[17] = "   "+location_tag+ ".PLU"
    l[18] = "   './DATA/'"

    l[19] = "   1.4 Atmospheric CO2 concentration (CO2) file"
    l[20]="   MaunaLoa.CO2"
    l[21]="   './SIMUL/'"

    l[22]="-- 2. Calendar (CAL) file"
    l[23]="   "+location_tag+".CAL"
    l[24]="   './DATA/'"
    l[25]="-- 3. Crop (CRO) file"
    l[26]="   "+cropfile+ " " 
    l[27]="   './DATA/' "
    l[28]="-- 4. Irrigation management (IRR) file"
    l[29]="   "+irrigationfile
    if irrigationfile == '(NONE)': 
        l[29]="   (None)"
    l[30]="   './DATA/'"
    if irrigationfile == '(NONE)': 
        l[30]="   (None)"
    l[31]="-- 5. Field management (MAN) file"
    l[32]="   (None)"
    l[33]="   (None)"
    l[34]="-- 6. Soil profile (SOL) file"
    l[35]="   (None)"
    l[36]="   (None)"
    l[37]="-- 7. Groundwater table (GWT) file"
    l[38]="   (None)"
    l[39]="   (None)"
    l[40]="-- 8. Initial conditions (SW0) file"
    l[41]="   (None)"
    l[42] ="   (None)"
    l[43]="-- 9. Off-season conditions (OFF) file"
    l[44]="   (None)"
    l[45]="   (None)"
    l[46]="-- 10. Field data (OBS) file"
    l[47]="   (None)"
    l[48]="   (None)"
    save_file( l , path+"/LIST/"+location_tag+ ".PRM")

    l = [location_tag+ ".PRM"]
    # ~ #save and empty output file, because it needs that to run aquacrop...
    save_file( l , path+"/LIST/ListProjects.txt")




def simAquaCrop( location_tag, path , start_date , stop_date ,  df , minimum_harvest_temperature , crop_file , irrigation_file):
    
    
    
    print( " getting sim files ready for year =" , start_date, stop_date) 
    # ~ print(df)
    assert( stop_date in df.index)
    make_sim_setup_files( location_tag,path, start_date  ,stop_date , df, crop_file , irrigation_file)
    os.system('cd ' + path + '\n' + './aquacrop')

    #now look at data 
    headerlist = [    'RunNr'   ,  'Day1'  , 'Month1'  ,  'Year1'   ,  'Rain'   ,   'ETo'    ,   'GD'   ,  'CO2'    ,  'Irri' ,  'Infilt'  , 'Runoff' ,   'Drain'  , 'Upflow'      ,  'E'   ,  'E/Ex'   ,    'Tr'   ,   'TrW'  , 'Tr/Trx'  ,  'SaltIn'  , 'SaltOut'  ,  'SaltUp' , 'SaltProf'   ,  'Cycle'  , 'SaltStr' , 'FertStr' , 'WeedStr' , 'TempStr'  , 'ExpStr'  , 'StoStr' , 'BioMass' , 'Brelative'  , 'HI'   , 'Y(dry)' , 'Y(fresh)'    ,"WPet"   ,   'Bin' ,    'Bout' ,    'DayN' ,  'MonthN' ,   'YearN' ,'file']
    #I have to give this as a huge list because the .OUT format is not consistent with how many spaces it uses for variable seperation.  
    daily_header =[  'Day','Month' , 'Year'  , 'DAP', 'Stage'  , 'WC(1.20)a'  , 'Raina'  ,   'Irri' ,  'Surf'  , 'Infilt'  , 'RO'   , 'Drain'    ,   'CR'  ,  'Zgwta'    ,   'Ex'    ,  'E'   ,  'E/Ex'   ,  'Trxa' ,      'Tra' , 'Tr/Trx',    'ETx'   ,   'ET' , 'ET/ETx'   ,   'GD'    ,   'Za'  ,  'StExp' , 'StSto' , 'StSen' ,'StSalta', 'StWeed'  , 'CC'    ,  'CCw'   ,  'StTr' , 'Kc(Tr)'   ,  'Trxb'   ,    'Trb'    ,  'TrW'  ,'Tr/Trxb'  , 'WP'  ,  'Biomass'  ,   'HI'  ,  'Y(dry)' , 'Y(fresh)' , 'Brelative'  ,  'WPet'   ,   'Bin'    , 'Bout' ,'WC(1.20)b' ,'Wr(0.40)'   , 'Zb'   ,   'Wr'  ,  'Wr(SAT)'  ,  'Wr(FC)' ,  'Wr(exp)'  , 'Wr(sto)'  , 'Wr(sen)' ,  'Wr(PWP)'   , 'SaltIn'  ,  'SaltOut' ,  'SaltUp'  , 'Salt(1.20)' , 'SaltZ'   ,  'Zc'    ,   'ECe'  ,  'ECsw'  , 'StSaltb' , 'Zgwtb'   , 'ECgw'     ,  'WC01'    ,   'WC 2'    ,   'WC 3'    ,   'WC 4'    ,   'WC 5'      , 'WC 6'     ,  'WC 7'     ,  'WC 8'      , 'WC 9'    ,  'WC10'    ,   'WC11'   ,    'WC12'   ,   'ECe01'   ,   'ECe 2'   ,   'ECe 3'   ,   'ECe 4'   ,   'ECe 5'   ,  'ECe 6'   ,   'ECe 7'   ,  'ECe 8'    ,  'ECe 9'   ,   'ECe10'   ,   'ECe11'    ,  'ECe12'   ,  'Rainb'    ,   'ETo'    ,  'Tmin'    ,  'Tavg'   ,   'Tmax'     , 'CO2']
    #these next rows are just here for debugging, i had to rename some to avoid doubles
                        # ~ Day Month     Year       DAP   Stage       WC(1.20)       Rain        Irri      Surf      Infilt       RO      Drain          CR       Zgwt            Ex       E         E/Ex        Trx             Tr     Tr/Trx      ETx         ET     ET/ETx         GD          Z        StExp     StSto     StSen    StSalt     StWeed      CC        CCw         StTr     Kc(Tr)        Trx           Tr          TrW      Tr/Trx      WP        Biomass        HI      Y(dry)     Y(fresh)     Brelative        WPet        Bin         Bout    WC(1.20)     Wr(0.40)      Z          Wr       Wr(SAT)       Wr(FC)      Wr(exp)      Wr(sto)      Wr(sen)      Wr(PWP)       SaltIn       SaltOut      SaltUp      Salt(1.20)      SaltZ       Z           ECe       ECsw      StSalt     Zgwt        ECgw          WC01          WC 2          WC 3          WC 4          WC 5          WC 6          WC 7          WC 8          WC 9         WC10          WC11          WC12         ECe01         ECe 2         ECe 3         ECe 4         ECe 5         ECe 6         ECe 7       ECe 8         ECe 9         ECe10         ECe11         ECe12        Rain           ETo          Tmin        Tavg        Tmax          CO2
                                      # ~ mm      mm       mm     mm     mm     mm       mm       mm      m        mm       mm     %        mm       mm    %        mm      mm       %  degC-day     m       %      %      %      %      %      %       %       %       -        mm       mm       mm    %     g/m2    ton/ha      %    ton/ha   ton/ha       %       kg/m3   ton/ha   ton/ha      mm       mm       m       mm        mm        mm        mm        mm        mm         mm    ton/ha    ton/ha    ton/ha    ton/ha    ton/ha     m      dS/m    dS/m      %     m      dS/m       0.05       0.15       0.25       0.35       0.45       0.55       0.65       0.75       0.85       0.95       1.05       1.15       0.05       0.15       0.25       0.35       0.45       0.55       0.65       0.75       0.85       0.95       1.05       1.15       mm        mm     degC      degC      degC       ppm
                        # ~ 1     1       2017       1      1          359.3           0.0         0.0      0.0        0.0         0.0      0.0           0.0     -9.90            0.7      0.7       97          0.0             0.0     100         0.7        0.7      97           11.5       0.30       -9         0         0        0         0          1.2       1.2          0        0.02          0.0          0.0         0.0       100       18.6       0.004         -9.9      0.000      0.000        100              0.00      0.000       0.000     359.3        119.3       0.30        89.3     150.0      90.0      65.7      52.3      35.1      30.0    0.000     0.000     0.000     0.000     0.000    0.30     0.00    0.00      0   -9.90   -9.00       29.3       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0       30.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0        0.0      0.0       0.6       6.0      15.5      25.0    406.77
 


    dfout = pd.read_csv( path+"/OUTP/" + location_tag+ "PRMday.OUT", skiprows = 5, names= daily_header, sep="\\s+"  , index_col=None )
    
    dfout['dateobject'] = pd.to_datetime(dict(year=dfout.Year, month=dfout.Month, day=dfout.Day))
    dfout['timestamp'] = dfout['dateobject'].apply(pd.Timestamp)
    dfout['timestamp'] = pd.to_numeric(dfout['timestamp']) / 1E9
    # ~ print(dfout['timestamp'])
    # ~ dfout['dateobject'] = dfout['dateobject'].to_datetime()
    
    dfout["DAP"] = pd.to_numeric(dfout["DAP"])
    
    #option one- yeild when crop is mature, truncate dfout there
    #option 2 - yield when temp min falls below minimum harvest temperature, truncate dfout there 
    cropendindex = df.index[-1] #first guess is it's the end of the input file date. 
    for i , ival in enumerate(dfout.index):
        if (dfout['Tmin'].loc[ival] < minimum_harvest_temperature):
            cropendindex = ival
            break

            
    cropmatureindex = dfout['DAP'].idxmax() #find index when DAP is greatest
    if cropmatureindex < cropendindex:
        cropendindex = cropmatureindex
    
    dfout = dfout.loc[dfout.index[0]:cropendindex]
    return dfout

   
