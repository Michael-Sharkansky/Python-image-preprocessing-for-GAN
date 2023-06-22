# erase, copy or move files in the multiple parallel folders at the same time.
# The selections of from line “i” to line “j” will process the i-th line, the j-th line and all the lines between them: j-i+1 images.
#Programmed by Michael Sharkansky

import os
import argparse
import cv2  # use: pip install opencv-contrib-python
import shutil
import time
import numpy as np

#GUI with tkinter, see https://likegeeks.com/python-gui-examples-tkinter-tutorial/
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog

# construct the argument parser and parse the arguments --------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=False, help="Path to the configuration file")
args = vars(ap.parse_args())
print("Conf: ",args["conf"])
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)

folders=[]
files=[]
current_file=0
base_dir=""

# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Erase / Copy / Move out files from folders to other folders")
window.geometry('1150x420')  # window size


entry_from = Entry(window, width=100)  # THE FILE NAME INPUT widget
entry_from.grid(column=2, row=0)  # location within the window
entry_from.insert(0, "")

combo_action = Combobox(window, width=16, state='readonly')
combo_action['values'] = ("Select?","Erase",  "Copy",  "Move", "List")      # actions
combo_action.current(0)  # set the selected item
combo_action.grid(column=0, row=1)

chk_verb=BooleanVar()     # verbose
chk_verb.set(False)
chk_box_verb = Checkbutton(window, text="Verbose:", var=chk_verb)
chk_box_verb.grid(column=2, row=1)

label_1 = Label(window, anchor=E, text="From line (0-All):")
label_1.grid(column=0, row=2)   # widget's location

entry_line1 = Entry(window, width=8)  # skip files  widget
entry_line1.grid(column=1, row=2)  # location within the window
entry_line1.insert(0, "0")

label_2 = Label(window, anchor=E, text="To line (0-All):")
label_2.grid(column=0, row=3)   # widget's location

entry_line2 = Entry(window, width=8)  # skip files  widget
entry_line2.grid(column=1, row=3)  # location within the window
entry_line2.insert(0, "0")

entry_to = Entry(window, width=100)  # THE FILE NAME INPUT widget
entry_to.grid(column=2, row=15)  # location within the window
entry_to.insert(0, "")

chk_file=BooleanVar()     # do for a single file
chk_file.set(False)
chk_box_file = Checkbutton(window, text="One file:", var=chk_file)
chk_box_file.grid(column=1, row=16)

entry_file = Entry(window, width=100)  # THE FILE NAME INPUT widget
entry_file.grid(column=2, row=16)  # location within the window
entry_file.insert(0, "")


label_state = Label(window, text="Waiting for selection of Source and Target folders.")
label_state.grid(column=2, row=17)

if args["conf"] is not None:        # load the config file with predefined foler names
    config=args.get("conf","")
    if not os.path.isfile(config):
        config=os.path.join(os.path.dirname(os.path.realpath(__file__)), config)
    print("Loading config: ",config)
    if os.path.isfile(config):
        in_conf = open(config, 'rt')
        lin1=in_conf.readline()[:-1]
        base_dir=in_conf.readline()[:-1]    # input folder
        lin2=in_conf.readline()[:-1]
        out_dir=in_conf.readline()[:-1]   # output sub-folder
        in_conf.close()
        print("Loaded.")
        entry_from.delete(0,END)                    #clear the widget
        entry_from.insert(0, base_dir)              #put text into the entry widget
        entry_to.delete(0,END)                      #clear the widget
        entry_to.insert(0, out_dir)                 #put text into the entry widget
        label_state.configure(text="Folders are set.")  # show on the GUI screen           
    else:
        config=""
        print("config not loaded")


def from_folders():
    the_dir=""
    the_dir = filedialog.askdirectory(title="From Folder")

    entry_from.delete(0,END)               #clear the widget
    entry_from.insert(0, the_dir)             #put text into the entry widget
    entry_from.focus()                     # SET IN FOCUS
    label_state.configure(text="Source folder set.")  # show on the GUI screen
    print(the_dir)
    if not os.path.exists(the_dir):			
        label_state.configure(text="Source folder not found.")

def to_folders():
    the_dir=""
    the_dir = filedialog.askdirectory(title="To Folder")

    entry_to.delete(0,END)               #clear the widget
    entry_to.insert(0, the_dir)             #put text into the entry widget
    entry_to.focus()                     # SET IN FOCUS
    label_state.configure(text="Target folder set.")  # show on the GUI screen			
    if not os.path.exists(the_dir):			
        label_state.configure(text="Target folder not found.")


def go():
   if chk_file.get() :
        go_one_file()
   else:
        go_many()

def go_many():
    from_folder=entry_from.get()  #get input file from gui
    to_folder=entry_to.get()  #get input file from gui
    if not (os.path.exists(from_folder) and os.path.exists(to_folder)) :			
        label_state.configure(text="Source or Target folder not found.")
        return
    count=0
    from_count=int(entry_line1.get()) 
    to_count=int(entry_line2.get()) 
    selected = combo_action.get()
    if selected=="Select?":
        label_state.configure(text="No action was selected.")  # show on the GUI screen           
        return
     # r=root, d=directories, f = files
    for r, d, f in os.walk(from_folder):
        for folder in d:
            #folders.append(folder)
            print("input base folder ", folder)
            results_dir = os.path.join(to_folder , folder)
            if not (selected == "Erase") and not os.path.exists(results_dir):
                os.mkdir(results_dir)
                print("create ", results_dir)
                # r=root, d=directories, f = files
            count=0
            for r, d, f in os.walk(os.path.join(from_folder,folder)):
                for file in f:
                    count=count+1
                    if (from_count==0 and to_count==0) or (count>=from_count and count<=to_count):
                        #if '.jpg' or '.JPG' or '.png' or'.PNG' or '.bmp' or  '.BMP' in file:
                        file1=os.path.join(os.path.join(from_folder,folder), file)
                        if selected == "Erase":
                            os.remove(file1)
                            print(file1, " removed")
                        if selected == "Copy":
                            file2=os.path.join(results_dir ,file)
                            shutil.copy2(file1,file2)
                            print(file1, " copied ",file2)
                        if selected == "Move":
                            file2=os.path.join(results_dir ,file)
                            shutil.move(file1, file2)   # move file to another folder
                            print(file1, " moved ",file2)
                        if selected == "List":
                            print("{} {}".format(count,file1))
    label_state.configure(text="Done, {} files.".format(count))  # show on the GUI screen

    
def go_one_file():
    from_folder=entry_from.get()  #get input file from gui
    to_folder=entry_to.get()  #get input file from gui
    file=entry_file.get()
    selected = combo_action.get()
    if selected=="Select?":
        label_state.configure(text="No action was selected.")  # show on the GUI screen           
        return
     # r=root, d=directories, f = files
    for r, d, f in os.walk(from_folder):
        for folder in d:
            #folders.append(folder)
            print("input base folder ", folder)
            results_dir = os.path.join(to_folder , folder)
            if not selected == "Erase" and not os.path.exists(results_dir):
                os.mkdir(results_dir)
                print("create ", results_dir)
            # r=root, d=directories, f = files
            count=0
            for r, d, f in os.walk(os.path.join(from_folder,folder)):
                #if '.jpg' or '.JPG' or '.png' or'.PNG' or '.bmp' or  '.BMP' in file:
                file1=os.path.join(os.path.join(from_folder,folder), file)
                if os.path.exists(file1):
                    if selected == "Erase":
                        os.remove(file1)
                        print(file1, " removed")
                    if selected == "Copy":
                        file2=os.path.join(results_dir ,file)
                        shutil.copy2(file1,file2)
                        print(file1, " copied ",file2)
                    if selected == "Move":
                        file2=os.path.join(results_dir ,file)
                        shutil.move(file1, file2)   # move file to another folder
                        print(file1, " moved ",file2)
    label_state.configure(text="Done.")  # show on the GUI screen           

button_init = Button(window, text="Source", bg="green", fg="blue", command=from_folders)
button_init.grid(column=1, row=0)

button_to = Button(window, text="Target", bg="green", fg="blue", command=to_folders)
button_to.grid(column=1, row=15)

button_to = Button(window, text="Go", bg="orange", fg="red", command=go)
button_to.grid(column=0, row=17)



window.mainloop()   #run the window loop

#termination

sys.exit(0)
