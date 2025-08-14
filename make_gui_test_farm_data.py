#make a gui testing farm_data class 
# ~ import sys
# ~ import os
# ~ sys.path.append(os.path.abspath('../'))

from soil_plot import *
s = soil_plot()
s.details['id'] = "testid"
s.details['soil_type'] = "bare rock"

from crop_plan import * 

lettuce_plan = crop_plan()
lettuce_plan.soil_plots.append(s)
lettuce_plan.event_list.append( demo1_crop_event() )
lettuce_plan.event_list.append( demo2_crop_event() )
lettuce_plan.event_list.append( demo3_crop_event() )
lettuce_plan.event_list.append( demo4_crop_event() )
lettuce_plan.event_list.append( demo5_crop_event() )

#make the dates for today: 
lettuce_plan.event_list[0].details['planned_timestamp'] = time.time() - 24*60*60 
lettuce_plan.event_list[1].details['planned_timestamp'] = time.time()  
lettuce_plan.event_list[2].details['planned_timestamp'] = time.time() + 24*60*60 


from farm_data import *
my_farm = farm_data()
my_farm.details["farm_name"] = "gui_test_farm"
my_farm.details["farm_address"] = "cyberspace"
my_farm.active_crop_plan_list.append( lettuce_plan)


##ok now I have a farm data, I will use that


import tkinter as tk
from tkinter import scrolledtext 
from tkinter import Listbox ,Scrollbar, SINGLE , END, LEFT,RIGHT,BOTH

import datetime 
import calendar
# ~ from datetime import datetime, timezone


##this is code for actually setting up values etc, not just formating 
today = datetime.date.today()
todaytimestamp = calendar.timegm(today.timetuple()) #stamp for mighnight, start of today in gmt

yesterday = today - datetime.timedelta(days = 1 )
tomorrow = today + datetime.timedelta(days = 1 )
# Textual month, day and year	
today_string = today.strftime("%d %B %Y")
yesterday_string = yesterday.strftime("%d %B %Y")
tomorrow_string = tomorrow.strftime("%d %B %Y")

days = [yesterday_string , today_string , tomorrow_string] 

    
###look through the all the crop plans, and add to these lists. 
#we need a function that updates these from the farm_data so I can call it to refresh
def event_titles( fd , current_day_start_timestamp ):#current day is a datetime.date.today thing
    daysecs = 24*60*60
    today_limits = [ current_day_start_timestamp , current_day_start_timestamp+ daysecs] 
    yesterday_limits = [ current_day_start_timestamp-daysecs , current_day_start_timestamp] 
    tomorrow_limits = [ current_day_start_timestamp+daysecs , current_day_start_timestamp+daysecs*2] 
    
    out_yesterday = []
    out_today = []
    out_tomorrow = []
    
    #walk through all the active crop plans:
    for i, cp in enumerate(fd.active_crop_plan_list):
        #walk through all the events: 
        for j, ev in enumerate(cp.event_list): 
            #look at planned time stamp
            if ev.details['planned_timestamp'] > yesterday_limits[0] and ev.details['planned_timestamp'] <= yesterday_limits[1]:
                #this is a yesterday event. 
                title = cp.cultivar.details['name'] + " " +ev.details['event_name']
                if ev.details['is_finished'] == False and ev.details['actual_timestamp_start'] == -1:
                    pass 
                if ev.details['is_finished'] == False and ev.details['actual_timestamp_start'] > 0:
                    title = "PART FINSIHED- " + title 
                if ev.details['is_finished'] == True: 
                    title = "FINSIHED- " + title
                temp_list = [ i , j , title]
                out_yesterday.append(temp_list)
                
            if ev.details['planned_timestamp'] > today_limits[0] and ev.details['planned_timestamp'] <= today_limits[1]:
                #this is a today event. 
                title = cp.cultivar.details['name'] + " "+ev.details['event_name']
                if ev.details['is_finished'] == False and ev.details['actual_timestamp_start'] == -1:
                    pass 
                if ev.details['is_finished'] == False and ev.details['actual_timestamp_start'] > 0:
                    title = "PART FINSIHED- " + title 
                if ev.details['is_finished'] == True: 
                    title = "FINSIHED- " + title
                temp_list = [ i , j , title]
                out_today.append(temp_list)
                
            if ev.details['planned_timestamp'] > tomorrow_limits[0] and ev.details['planned_timestamp'] <= tomorrow_limits[1]:
                #this is a today event. 
                title = cp.cultivar.details['name'] + " " + ev.details['event_name']
                if ev.details['is_finished'] == False and ev.details['actual_timestamp_start'] == -1:
                    pass 
                if ev.details['is_finished'] == False and ev.details['actual_timestamp_start'] > 0:
                    title = "PART FINSIHED- " + title 
                if ev.details['is_finished'] == True: 
                    title = "FINSIHED- " + title
                temp_list = [ i , j , title]
                out_tomorrow.append(temp_list)
    
    return out_yesterday, out_today , out_tomorrow
            
    #return list of i,j,title 
print( event_titles(my_farm , todaytimestamp))

def get_event_details( fd , i , j ):
    ev = fd.active_crop_plan_list[i].event_list[j]
    
    task_description = ev.details['human_instructions']
    tool_list = ev.details['tools used'] 
    consumable_list = ev.details['consumables_used'] 
    timestamp_start = ev.details['actual_timestamp_start']
    timestamp_stop = ev.details['actual_timestamp_end'] 
    
def get_event( fd, i, j): 
    return fd.active_crop_plan_list[i].event_list[j]

def update_event( fd , i , j , ev):
    fd.active_crop_plan_list[i].event_list[j] = ev
    return fd 
       

    
event_list_1= ["FINISHED- sow carrots" , "weed lettuce" , "PARTLY FINISHED-pick peas" ,"blah" ,"blah","blah","blah","blah","blah","blah","blah","blah","blah","blah","blah","blah"] 
event_list_2= ["pick lettuce" , "weed lettuce" , "pick peas" ] 
event_list_3= ["wash lettuce" , "weed lettuce" , "pick peas" ] 
list_of_daily_events = [ event_list_1, event_list_2, event_list_3]

dummy_task_descriptions = ["Go pull out the weeds. use a hoe in the open areas. " , "Bring a basket, cut the heads of lettuce and put them in" ]
dummy_tool_list = ["hoe" , "boots" , "basket for weeds" , "sun hat" ] 
dummy_comment = "It was fine, but the sun was in my eyes. maybe I need a better hat"

window_title = 'Do Farm Task - Carl'
dummy_task_start_time = "21 jan 2025 \n 11:30 am \n atlantic time"
dummy_task_start_time = "No task \n currently running"
dummy_elapsed_time = "00h00m00s"

###start making the gui

root = tk.Tk()
root.title(window_title)
tot_width = 1000 
tot_height = 800

frm_all_top = tk.Frame( master = root) #this is a grid of tasks for each day
frm_all_top.pack()
frm_all_low = tk.Frame( master = root) #this is all the stuff to do one task that's been selected 
frm_all_low.pack()

##using grids. So first make 3 frames for each of the columns (days) 
top_row_frms = []
for i, d in enumerate(days):
    frm_top = tk.Frame( master = frm_all_top)
    top_row_frms.append(frm_top)
    
    lbl_temp = tk.Label(top_row_frms[i], text= d, width=40, height=5) #text is a lable with human readable date 
    lbl_temp.pack()
    
    top_row_frms[i].grid(row=0, column=i)
        


#so each day needs to have a drop down list to select task. It needs to have finished_tag +" "+cultivar_name +" "+ human_event_description in each one. 

for i, d in enumerate(days):
    frm_temp= tk.Frame( master = frm_all_top)
    
    # ~ variable = tk.StringVar(root)
    # ~ variable.set(event_list_1[0]) # default value
    
    
    # Creating a Listbox and 
    # attaching it to root window 
    listbox = Listbox(frm_temp , selectmode=SINGLE, width = 50) 
      
    # Adding Listbox to the left 
    # side of root window 
    listbox.pack(side = LEFT, fill = BOTH) 
      
    # Creating a Scrollbar and  
    # attaching it to root window 
    scrollbar = Scrollbar(frm_temp) 
      
    # Adding Scrollbar to the right 
    # side of root window 
    scrollbar.pack(side = RIGHT, fill = BOTH) 
      
    # Insert elements into the listbox 
    for n in list_of_daily_events[i]: 
        listbox.insert(END, n) # put tasks for that day in the thing
          
    # Attaching Listbox to Scrollbar 
    # Since we need to have a vertical  
    # scroll we use yscrollcommand 
    listbox.config(yscrollcommand = scrollbar.set) 
      
    # setting scrollbar command parameter  
    # to listbox.yview method its yview because 
    # we need to have a vertical view 
    scrollbar.config(command = listbox.yview) 
        

    frm_temp.grid( row= 1, column = i )

for i, d in enumerate(days):
    frm_temp= tk.Frame( master = frm_all_top)
    
    button = tk.Button(frm_temp , text="Start Task")
    button.pack()
    
    frm_temp.grid( row= 2, column = i )

#now looking at the bottom main frame, this stuff changes depending on what you select as the task and hit start. 

##left to right: Task description, list of tools, task location - eventually this is going to be a map, for now blank, comment section , buttons to auto fill comments with other recent comment text (save typing time)

##description 
frm_description = tk.Frame(master = frm_all_low) 
frm_description.pack(side = 'left')  
lbl_temp = tk.Label(frm_description, text= dummy_task_descriptions[0], width=60, height=10)
lbl_temp.pack()

#list of tools. 
list_string = ""
for t in dummy_tool_list:
    list_string += t + '\n'
frm_tool_list = tk.Frame(master = frm_all_low) 
frm_tool_list.pack(side = 'left')  
lbl_temp = tk.Label(frm_tool_list, text= list_string, width=30, height=10)
lbl_temp.pack()

##map 
frm_map = tk.Frame(master = frm_all_low) 
frm_map.pack(side = 'left') 


##comment section 
frm_comments = tk.Frame(master = frm_all_low)
frm_comments.pack(side = 'left')
textBox = scrolledtext.ScrolledText(frm_comments,  
                                      wrap = tk.WORD,  
                                      width = 40,  
                                      height = 10) 
                                    

textBox.insert(tk.INSERT, dummy_comment) 
textBox.pack()  

##buttons right 
frm_buttons = tk.Frame(master = frm_all_low)
frm_buttons.pack(side = 'left')

button = tk.Button(frm_buttons , text="Back \n Description")
button.pack()

button = tk.Button(frm_buttons , text="Next \n Description")
button.pack()

button = tk.Button(frm_buttons , text="Task \n Finished")
button.pack()

button = tk.Button(frm_buttons , text="Task Partly \n Finished")
button.pack()

##Time Started and current task 
frm_current = tk.Frame(master = frm_all_low) 
frm_current.pack(side = 'left')  
lbl_start_time = tk.Label(frm_current, text= dummy_task_start_time, width=15, height=3)
lbl_elapsed_time = tk.Label(frm_current, text= dummy_elapsed_time, width=15, height=1)
lbl_start_time.pack()
lbl_elapsed_time.pack()


root.mainloop()
