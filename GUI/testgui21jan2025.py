#testing how to make a gui in python

# ~ import PySimpleGUI as sg

# ~ # All the stuff inside your window.
# ~ layout = [  [sg.Text('Some text on Row 1')],
            # ~ [sg.Text('Enter something on Row 2'), sg.InputText()],
            # ~ [sg.Button('Ok'), sg.Button('Cancel')] ]

# ~ # Create the Window
# ~ window = sg.Window('Window Title', layout)

# ~ # Event Loop to process "events" and get the "values" of the inputs
# ~ while True:
    # ~ event, values = window.read()
    # ~ if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        # ~ break
    # ~ print('You entered ', values[0])

# ~ window.close()


#https://realpython.com/python-gui-tkinter/
import tkinter as tk
from tkinter import scrolledtext 

import datetime 


today = datetime.date.today()
yesterday = today - datetime.timedelta(days = 1 )
tomorrow = today + datetime.timedelta(days = 1 )
# Textual month, day and year	
today_string = today.strftime("%d %B %Y")
yesterday_string = yesterday.strftime("%d %B %Y")
tomorrow_string = tomorrow.strftime("%d %B %Y")

days = [yesterday_string , today_string , tomorrow_string] 

root = tk.Tk()
root.title('Do Farm Task')
tot_width = 1000 
tot_height = 800

frm_all_top = tk.Frame( master = root)
frm_all_top.pack()
frm_all_low = tk.Frame( master = root)
frm_all_low.pack()

##using grids. So first make 3 frames for each of the columns (days) 
top_row_frms = []

for i, d in enumerate(days):
    frm_top = tk.Frame( master = frm_all_top)
    # ~ lbl_temp = tk.Label(master=frm_top, text= d, width=40, height=5)
    # ~ lbl_temp.pack()
    top_row_frms.append(frm_top)
    
    lbl_temp = tk.Label(top_row_frms[i], text= d, width=40, height=5)
    lbl_temp.pack()
    
    top_row_frms[i].grid(row=0, column=i)
    
##ok now I have a list of frames, packed into a grid 

##TODO make a single fram under the grid stuff... possible? Maybe I need two frames to start with, top and bottom, put the grid into the top one... that sounds plausible
    


    
event_list_1= ["FINISHED- sow carrots" , "weed lettuce" , "pick peas" ] 
event_list_2= ["pick lettuce" , "weed lettuce" , "pick peas" ] 
event_list_3= ["wash lettuce" , "weed lettuce" , "pick peas" ] 
list_of_daily_events = [ event_list_1, event_list_2, event_list_3]

dummy_task_descriptions = ["Go pull out the weeds. use a hoe in the open areas. " , "Bring a basket, cut the heads of lettuce and put them in" ]
dummy_tool_list = ["hoe" , "boots" , "basket for weeds" , "sun hat" ] 
dummy_comment = "It was fine, but the sun was in my eyes. maybe I need a better hat"

#so each day needs to have a drop down list to select task. It needs to have finished_tag +" "+cultivar_name +" "+ human_event_description in each one. 

for i, d in enumerate(days):
    frm_temp= tk.Frame( master = frm_all_top)
    
    variable = tk.StringVar(root)
    variable.set(event_list_1[0]) # default value

    w = tk.OptionMenu(frm_temp, variable, *list_of_daily_events[i])
    w.pack()
    
    button = tk.Button(frm_temp , text="Start Task")
    button.pack()
    
    frm_temp.grid( row= 1, column = i )

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

##description 
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
frm_buttons.pack(side = 'right')

button = tk.Button(frm_buttons , text="Back \n Description")
button.pack()

button = tk.Button(frm_buttons , text="Next \n Description")
button.pack()

button = tk.Button(frm_buttons , text="Task \n Finished")
button.pack()




root.mainloop()
