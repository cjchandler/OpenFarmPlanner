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
# ~ root.geometry(str(tot_width) + 'x' + str(tot_height)+'+150+50')
for d in days:
    frm_top = tk.Frame( master = root)
    frm_top.pack(side = tk.LEFT) 
    lbl_temp = tk.Label(master=frm_top, text= d, width=40, height=5)
    lbl_temp.pack()
    
event_list_1= ["FINISHED- sow carrots" , "weed lettuce" , "pick peas" ] 
event_list_2= ["pick lettuce" , "weed lettuce" , "pick peas" ] 
#so each day needs to have a drop down list to select task. It needs to have finished_tag +" "+cultivar_name +" "+ human_event_description in each one. 

for d in days: 
    frm_top = tk.Frame( master = root)
    frm_top.pack(side = tk.LEFT)
    
    variable = tk.StringVar(root)
    variable.set(event_list_1[0]) # default value

    w = tk.OptionMenu(frm_top, variable, *event_list_1)
    w.pack()


button = tk.Button(
    text="Click me!",
    width=25,
    height=5,
    bg="blue",
    fg="yellow",
)

root.mainloop()
