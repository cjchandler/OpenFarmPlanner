# Test GUI for doing a farm task


import tkinter as tk
from tkinter import scrolledtext 
from tkinter import Listbox ,Scrollbar, SINGLE , END, LEFT,RIGHT,BOTH

import datetime 

##this is code for actually setting up values etc, not just formating 
today = datetime.date.today()
yesterday = today - datetime.timedelta(days = 1 )
tomorrow = today + datetime.timedelta(days = 1 )
# Textual month, day and year	
today_string = today.strftime("%d %B %Y")
yesterday_string = yesterday.strftime("%d %B %Y")
tomorrow_string = tomorrow.strftime("%d %B %Y")

days = [yesterday_string , today_string , tomorrow_string] 

    
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
