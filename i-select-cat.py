#For GAN model data, any OS: 
#The purpose is to split [feature label] image set into several (up to 5) categories of images. 
#The best way is to run on the folder with appended feature/label images (Leading sub-folder). This folder of appended images can be created 
# by running i-append2.py program over the feature folder and the label folder.
#Run in a main folder and leave or move files to another folders, 
# take a file and possibly move all the files with this name from parallel folders to parallel folders in another directories:
# a/f/pic1.jpg -> b/f/pic1.jpg
# a/l/pic1.jpg -> b/l/pic1.jpg
# a/fl/pic1.jpg -> b/fl/pic1.jpg
# and so on for each selected file into any of the output category containig folders.
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
ap.add_argument("-i", "--path", required=False, help="Path to the images folder")
ap.add_argument("-c", "--conf", required=False, help="Path to the configuration file")
args = vars(ap.parse_args())
print("Base: ",args["path"])
print("Conf: ",args["conf"])
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)

folders=[]
files=[]
last_cat_dir=[]
current_file_index=0
current_file=0
first_file=True # force to count from 0-th file
first_dir=""
base_dir=""
out_dir1=""
out_dir2=""
out_dir3=""
out_dir4=""
out_dir5=""
last_dir=""
moved=0
config=""
count1=0
count2=0
count3=0
count4=0
count5=0

if args["conf"] is not None:        # load the config file with predefined foler names
    config=args.get("conf","")
    if not os.path.isfile(config):
        config=os.path.join(os.path.dirname(os.path.realpath(__file__)), config)
    print("Loading config: ",config)
    if os.path.isfile(config):
        in_conf = open(config, 'rt')
        lin1=in_conf.readline()[:-1]
        base_dir=in_conf.readline()[:-1]    # base folder 
        lin1=in_conf.readline()[:-1]
        first_dir=in_conf.readline()[:-1]   # leading sub-folder 
        lin1=in_conf.readline()[:-1]
        out_dir1=in_conf.readline()[:-1]    # cathegory folder 1
        lin1=in_conf.readline()[:-1]
        out_dir2=in_conf.readline()[:-1]    # cat folder 2
        lin1=in_conf.readline()[:-1]
        out_dir3=in_conf.readline()[:-1]    # cat folder 3
        lin1=in_conf.readline()[:-1]
        out_dir4=in_conf.readline()[:-1]    # cat folder 4
        lin1=in_conf.readline()[:-1]
        out_dir5=in_conf.readline()[:-1]    # cat folder 5
        in_conf.close()
        print("Loaded.")
    else:
        config=""
        print("config not loaded")


# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Move out images from folders to other folders by cathegories")
window.geometry('1150x420')  # window size


entry_current = Entry(window, width=100)  # THE FILE NAME INPUT widget
entry_current.grid(column=4, row=0)  # location within the window
entry_current.insert(0, "?")

entry_skip = Entry(window, width=8)  # skip files  widget
entry_skip.grid(column=1, row=3)  # location within the window
entry_skip.insert(0, "0")

chk_fit_big=BooleanVar()     # fit big image to window, good when selecting feature/label, can changed at any time
chk_fit_big.set(False)
chk_box_fit_big = Checkbutton(window, text="Fit big\nimage", var=chk_fit_big)
chk_box_fit_big.grid(column=3, row=6)

label_cat = Label(window, text="Categories:")
label_cat.grid(column=0, row=8)

label_moved = Label(window, text="****")    # counter of moved files
label_moved.grid(column=1, row=8)

label_lastg = Label(window, text="?")       # last group to where the file was moved
label_lastg.grid(column=3, row=8)

label_state = Label(window, text="Waiting for init.")
label_state.grid(column=4, row=8)

entry_action = Entry(window, width=8)  #
entry_action.grid(column=1, row=6)  # 
entry_action.insert(0, "-")



def load_folders():
    global base_dir, first_dir
    global moved, current_file_index,current_file, first_file
    if config=="":
        base_dir = filedialog.askdirectory(title="Parent folder to contain Input Folders")
        first_dir = filedialog.askdirectory(title="Leading sub-folder")
    print("input base ", base_dir)
    print("input base leading folder ", first_dir)
    folders.clear()
    files.clear()
    last_cat_dir.clear()
    moved=0
    current_file_index = 0
    current_file = 0
    first_file=True
    if base_dir==first_dir:
        text="Error: Base folder and leading folder are the same!"
        label_state.configure(text=text)  # show on the GUI screen
        return

    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            folders.append(folder)
            print("input base folder ", folder)
            #results_dir_f = os.path.join(out_dir , folder)
            #if not os.path.exists(results_dir_f):
            #    os.mkdir(results_dir_f)


    # r=root, d=directories, f = files
    for r, d, f in os.walk(first_dir):
        for file in f:
            if '.jpg' or '.JPG' or '.png' or'.PNG' or '.bmp' or  '.BMP' in file:
                files.append(os.path.join(r ,file))
                last_cat_dir.append("")

    print("{} files in each of {} folders like {}".format(len(files), len(folders), first_dir))
    #######


def run_move1():
    global current_file_index,current_file, inner_counter, moved, last_dir, out_dir1, count1
    if (out_dir1==""):
        return
    last_dir=out_dir1
    label_lastg.configure(text="1")  # show on the GUI screen
    moved=moved+1
    text = "{}".format(moved)
    label_moved.configure(text=text)  # show on the GUI screen
    infile = os.path.basename(current_file)
    entry_action.delete(0, END)
    entry_action.insert(0, "Next")
    last_cat_dir[current_file_index]=last_dir
    count1=count1+1   
    entry_current_1.delete(0, END)
    entry_current_1.insert(0, str(count1))
    print("{}/1 >>> {}/*/{} -> {}".format(current_file_index, base_dir, infile, out_dir1))
    for folder in folders:
        filename1=os.path.join(os.path.join(base_dir , folder) ,infile)
        filename2=os.path.join(os.path.join(last_dir , folder), infile) # set destination as full path name + filename to allow file overwrite
        #print("{}/1 >>> {} -> {}".format(moved, filename1, filename2))
        shutil.move(filename1, filename2)   # move file to another folder

def run_to1():
    global current_file_index,current_file, inner_counter, moved, out_dir1, count1
    if config=="":
        out_dir1 = filedialog.askdirectory(title="Parent folder to contain Output Folders /1")
    if out_dir1=="":
        return
    if not os.path.exists(out_dir1):
        os.mkdir(out_dir1)
    count1=0    
    entry_current_1.delete(0, END)
    entry_current_1.insert(0, str(count1))
    button_move_1["text"] = "1->"+os.path.split(out_dir1)[1]
    print("output base/1 ", out_dir1)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir1 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)

def run_move2():
    global current_file_index,current_file, inner_counter, moved, last_dir, count2
    if (out_dir2==""):
        return
    last_dir=out_dir2
    label_lastg.configure(text="2")  # 
    moved=moved+1
    text = "{}".format(moved)
    label_moved.configure(text=text)  # show on the GUI screen
    infile = os.path.basename(current_file)
    entry_action.delete(0, END)
    entry_action.insert(0, "Next")
    last_cat_dir[current_file_index]=last_dir
    count2=count2+1   
    entry_current_2.delete(0, END)
    entry_current_2.insert(0, str(count2))
    print("{}/2 >>> {}/*/{} -> {}".format(current_file_index, base_dir, infile, out_dir2))
    for folder in folders:
        filename1=os.path.join(os.path.join(base_dir , folder) ,infile)
        filename2=os.path.join(os.path.join(last_dir , folder), infile)
        #print("{}/2 >>> {} -> {}".format(moved, filename1, filename2))
        shutil.move(filename1, filename2)   # move file to another folder

def run_to2():
    global current_file_index,current_file, inner_counter, moved, out_dir2, count2
    if config=="":
        out_dir2 = filedialog.askdirectory(title="Parent folder to contain Output Folders /2")
    if out_dir2=="":
        return
    if not os.path.exists(out_dir2):
        os.mkdir(out_dir2)
    count2=0
    print("output base/2 ", out_dir2)
    entry_current_2.delete(0, END)
    entry_current_2.insert(0, str(count2))
    button_move_2["text"] = "2->"+os.path.split(out_dir2)[1]
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir2 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)

def run_move3():
    global current_file_index,current_file, inner_counter, moved,  last_dir, count3
    if (out_dir3==""):
        return
    last_dir=out_dir3
    label_lastg.configure(text="3")  # show on the GUI screen
    moved=moved+1
    text = "{}".format(moved)
    label_moved.configure(text=text)  # show on the GUI screen
    infile = os.path.basename(current_file)
    entry_action.delete(0, END)
    entry_action.insert(0, "Next")
    last_cat_dir[current_file_index]=last_dir
    count3=count3+1    
    entry_current_3.delete(0, END)
    entry_current_3.insert(0, str(count3))
    print("{}/3 >>> {}/*/{} -> {}".format(current_file_index, base_dir, infile, out_dir3))
    for folder in folders:
        filename1=os.path.join(os.path.join(base_dir , folder) ,infile)
        filename2=os.path.join(os.path.join(last_dir , folder), infile)
        shutil.move(filename1, filename2)   # move file to another folder

def run_to3():
    global current_file_index,current_file, inner_counter, moved, out_dir3, count3
    if config=="":
        out_dir3 = filedialog.askdirectory(title="Parent folder to contain Output Folders /3")
    if out_dir3=="":
        return
    if not os.path.exists(out_dir3):
        os.mkdir(out_dir3)
    count3=0
    entry_current_3.delete(0, END)
    entry_current_3.insert(0, str(count3))
    button_move_3["text"] = "3->"+os.path.split(out_dir3)[1]
    print("output base/3 ", out_dir3)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir3 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)

def run_move4():
    global current_file_index,current_file, inner_counter, moved,  last_dir, count4
    if (out_dir4==""):
        return
    last_dir=out_dir4
    label_lastg.configure(text="4")  # show on the GUI screen
    moved=moved+1
    text = "{}".format(moved)
    label_moved.configure(text=text)  # show on the GUI screen
    infile = os.path.basename(current_file)
    entry_action.delete(0, END)
    entry_action.insert(0, "Next")
    last_cat_dir[current_file_index]=last_dir
    count4=count4+1    
    entry_current_4.delete(0, END)
    entry_current_4.insert(0, str(count4))
    print("{}/4 >>> {}/*/{} -> {}".format(current_file_index, base_dir, infile, out_dir4))
    for folder in folders:
        filename1=os.path.join(os.path.join(base_dir , folder) ,infile)
        filename2=os.path.join(os.path.join(last_dir , folder), infile)
        shutil.move(filename1, filename2)   # move file to another folder

def run_to4():
    global current_file_index,current_file, inner_counter, moved, out_dir4, count4
    if config=="":
        out_dir4 = filedialog.askdirectory(title="Parent folder to contain Output Folders /4")
    if out_dir4=="":
        return
    if not os.path.exists(out_dir4):
        os.mkdir(out_dir4)
    count4=0
    entry_current_4.delete(0, END)
    entry_current_4.insert(0, str(count4))
    button_move_4["text"] = "4->"+os.path.split(out_dir4)[1]
    print("output base/4 ", out_dir4)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir4 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)

def run_move5():
    global current_file_index,current_file, inner_counter, moved,  last_dir, count5
    if (out_dir5==""):
        return
    last_dir=out_dir5
    label_lastg.configure(text="2")  # show on the GUI screen
    moved=moved+1
    text = "{}".format(moved)
    label_moved.configure(text=text)  # show on the GUI screen
    infile = os.path.basename(current_file)
    entry_action.delete(0, END)
    entry_action.insert(0, "Next")
    last_cat_dir[current_file_index]=last_dir
    count5=count5+1    
    entry_current_5.delete(0, END)
    entry_current_5.insert(0, str(count5))
    print("{}/5 >>> {}/*/{} -> {}".format(current_file_index, base_dir, infile, out_dir5))
    for folder in folders:
        filename1=os.path.join(os.path.join(base_dir , folder) ,infile)
        filename2=os.path.join(os.path.join(last_dir , folder), infile)
        shutil.move(filename1, filename2)   # move file to another folder

def run_to5():
    global current_file_index,current_file, inner_counter, moved, out_dir5, count5
    if config=="":
        out_dir5 = filedialog.askdirectory(title="Parent folder to contain Output Folders /5")
    if out_dir5=="":
        return
    if not os.path.exists(out_dir5):
        os.mkdir(out_dir5)
    count5=0
    entry_current_5.delete(0, END)
    entry_current_5.insert(0, str(count5))
    button_move_5["text"] = "5->"+os.path.split(out_dir5)[1]
    print("output base/5 ", out_dir5)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir5 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)


def run_back():
    global current_file_index, first_file
    entry_action.delete(0, END)
    entry_action.insert(0, "Next")
    if current_file_index>0:
        current_file_index = current_file_index - 1
    else:
        first_file=True         # force to count from 0-th file
    print("Back to {}".format(current_file_index))
        

def run_ctrl_z():   # move the files back to the original forlders
    global current_file_index,current_file, inner_counter, moved, last_dir
    moved=moved-1
    text = "{}".format(moved)
    label_moved.configure(text=text)  # show on the GUI screen
    infile = os.path.basename(current_file)
    entry_action.delete(0, END)
    entry_action.insert(0, "Next")
    last_dir=last_cat_dir[current_file_index]   # it was remebered where the file went to...
    for folder in folders:
        filename2=os.path.join(os.path.join(last_dir , folder) ,infile)
        filename1=os.path.join(base_dir , folder)
        print("{}/Undo >>> {} -> {}".format(current_file_index, filename2, filename1))
        shutil.move(filename2, filename1)   # move file back
    run_back()
           
  
def run_next():
    global current_file_index,current_file, inner_counter, first_file
    order=0
    if not first_file:                              # force to count from 0-th file
        current_file_index=current_file_index+1
    first_file=False
    if current_file_index<len(files):
        current_file=files[current_file_index]
        entry_current.delete(0, END)
        entry_current.insert(0, current_file)
        entry_action.delete(0, END)
        entry_action.insert(0, "Move")
        inner_counter=0
        entry_skip.delete(0, END)
        entry_skip.insert(0, str(current_file_index))

        text = "#{}: {}".format(current_file_index,current_file)
        label_state.configure(text=text)  # show on the GUI screen
        title="The Current Image"

        img = cv2.imread(current_file)
        #print(type(img))
        if not isinstance(img, np.ndarray):  #empty
            print("Not ndarray, empty image!")
            return
        bar_pos = 0
        if chk_fit_big.get():
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)  # ,cv2.WINDOW_KEEPRATIO) #fit to window size
        else:
            cv2.namedWindow(title)  # show as is, even when big
        cv2.imshow(title , img) # "The current picture"
        key= cv2.waitKey(0) & 0xFF
        cv2.destroyAllWindows()
        if key == ord("1") or key == 13 :  # enter key
            run_move1()
        if key == ord("2")  :  #
            run_move2()
        if key == ord("3")  :  # 
            run_move3()
        if key == ord("4")  :  # 
            run_move4()
        if key == ord("5")  :  # 
            run_move5()

    else:
        entry_current.delete(0, END)
        entry_current.insert(0, "")
        label_state.configure(text="No more files.")  # show on the GUI screen


def run_skip():
    global current_file_index
    current_file_index=current_file_index+int(entry_skip.get())  #
    print("Current index skip to: {}\n".format(current_file_index))

def run_config():
    if config=="":
        print("no config file passed\n");
        return
    load_folders()
    run_to1()
    run_to2()
    run_to3()
    run_to4()
    run_to5()

button_conf = Button(window, text="Config", bg="blue", fg="white", command=run_config)
button_conf.grid(column=0, row=2)

button_init = Button(window, text="Init Source", bg="orange", fg="red", command=load_folders)
button_init.grid(column=1, row=2)

button_init5 = Button(window, text="Skip", bg="orange", fg="blue", command=run_skip)
button_init5.grid(column=0, row=3)

label_3 = Label(window, anchor=E, text="-")
label_3.grid(column=0, row=4)   # widget's location

button_undo = Button(window, text="Undo Last", bg="orange", fg="blue", command=run_ctrl_z)
button_undo.grid(column=1, row=5)


button_init4 = Button(window, text="One Back", bg="orange", fg="blue", command=run_back)
button_init4.grid(column=0, row=6)

button_next0 = Button(window, text="Next", bg="orange", fg="blue", command=run_next)
button_next0.grid(column=2, row=8)

entry_current_1 = Entry(window, width=10)  
entry_current_1.grid(column=2, row=9) 
entry_current_1.insert(0, "")
button_move_1 = Button(window, text="Move 1", bg="orange", fg="blue", command=run_move1) # move to its folders
button_move_1.grid(column=1, row=9)
button_init_1 = Button(window, text="Init 1", bg="orange", fg="red", command=run_to1)  # initialize this output folder
button_init_1.grid(column=3, row=9)
button_next_1 = Button(window, text="Next", bg="orange", fg="blue", command=run_next)
button_next_1.grid(column=0, row=9)


entry_current_2 = Entry(window, width=10)  
entry_current_2.grid(column=2, row=10) 
entry_current_2.insert(0, "")
button_move_2 = Button(window, text="Move 2", bg="orange", fg="blue", command=run_move2)
button_move_2.grid(column=1, row=10)
button_init_2 = Button(window, text="Init 2", bg="orange", fg="red", command=run_to2)
button_init_2.grid(column=3, row=10)
button_next_2 = Button(window, text="Next", bg="orange", fg="blue", command=run_next)
button_next_2.grid(column=0, row=10)


entry_current_3 = Entry(window, width=10)  
entry_current_3.grid(column=2, row=11) 
entry_current_3.insert(0, "")
button_move_3 = Button(window, text="Move 3", bg="orange", fg="blue", command=run_move3)
button_move_3.grid(column=1, row=11)
button_init_3 = Button(window, text="Init 3", bg="orange", fg="red", command=run_to3)
button_init_3.grid(column=3, row=11)
button_next_3 = Button(window, text="Next", bg="orange", fg="blue", command=run_next)
button_next_3.grid(column=0, row=11)


entry_current_4 = Entry(window, width=10)  
entry_current_4.grid(column=2, row=12) 
entry_current_4.insert(0, "")
button_move_4 = Button(window, text="Move 4", bg="orange", fg="blue", command=run_move4)
button_move_4.grid(column=1, row=12)
button_init_4 = Button(window, text="Init 4", bg="orange", fg="red", command=run_to4)
button_init_4.grid(column=3, row=12)
button_next_4 = Button(window, text="Next", bg="orange", fg="blue", command=run_next)
button_next_4.grid(column=0, row=12)


entry_current_5 = Entry(window, width=10)  
entry_current_5.grid(column=2, row=13) 
entry_current_5.insert(0, "")
button_move_5 = Button(window, text="Move 5", bg="orange", fg="blue", command=run_move5)
button_move_5.grid(column=1, row=13)
button_init_5 = Button(window, text="Init 5", bg="orange", fg="red", command=run_to5)
button_init_5.grid(column=3, row=13)
button_next_5 = Button(window, text="Next", bg="orange", fg="blue", command=run_next)
button_next_5.grid(column=0, row=13)



window.mainloop()   #run the window loop

#termination

sys.exit(0)
