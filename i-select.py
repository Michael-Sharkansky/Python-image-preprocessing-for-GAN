# for GAN model data, any OS: run in a main folder and leave or move files to another folders, 
# take a file and possibly move all the files with this name from parallel folders to parallel folders in another directory:
# a/f/pic1.jpg -> b/f/pic1.jpg
# a/l/pic1.jpg -> b/l/pic1.jpg
# a/fl/pic1.jpg -> b/fl/pic1.jpg
# and so on for each selected file.
#The purpose is to clean image set of low quality images. The best way is to run on the folder with appended feature/label images.
#This folder of appended images can be created by running i-append.py over feature folder and label folder.
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
ap.add_argument("-i", "--path", required=False, help="Path to the input images folder")
ap.add_argument("-l", "--lead", required=False, help="Path to the images Leading folder")
ap.add_argument("-o", "--out", required=False, help="Path to the output images folder")
args = vars(ap.parse_args())
print(args["path"])
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)

folders=[]
files=[]
current_file_index=0
current_file=0
first_dir=""
base_dir=""
out_dir=""
moved=0
timeout=5000 # wait for key for 5 seconds

# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Move out images from folders to other folders")
window.geometry('950x250')  # window size


entry_current = Entry(window, width=90)  # THE FILE NAME INPUT widget
entry_current.grid(column=6, row=0)  # location within the window
entry_current.insert(0, "?")

entry_skip = Entry(window, width=8)  # skip files  widget
entry_skip.grid(column=1, row=3)  # location within the window
entry_skip.insert(0, "0")


chk_fit_big=BooleanVar()     # fit big image to window, good when selectinf feature/label, can changed at any time
chk_fit_big.set(False)
chk_box_fit_big = Checkbutton(window, text="Fit big\nimage", var=chk_fit_big)
chk_box_fit_big.grid(column=3, row=8)

label_moved = Label(window, text="****")
label_moved.grid(column=4, row=6)


label_state = Label(window, text="Waiting for init.")
label_state.grid(column=6, row=9)


def load_folders():
    global base_dir, out_dir
    global moved, current_file_index,current_file
    if args["path"] is not None:
        base_dir = args.get("path", "")
    else:
        base_dir = filedialog.askdirectory(title="Parent folder to contain Input Folders")
    if args["lead"] is not None:
        first_dir = args.get("lead", "")
    else:
        first_dir = filedialog.askdirectory(title="Leading sub-folder")
    if args["out"] is not None:
        out_dir = args.get("out", "")
    else:
        out_dir = filedialog.askdirectory(title="Parent folder to contain Output Folders")
    print("input base ", base_dir)
    print("input base leadind folder ", first_dir)
    print("output base ", out_dir)
    moved=0
    current_file_index = 0
    current_file = 0


    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)
            folders.append(folder)
            print("input base folder ", results_dir_f)


    # r=root, d=directories, f = files
    for r, d, f in os.walk(first_dir):
        for file in f:
            if '.jpg' or '.JPG' or '.png' or'.PNG' or '.bmp' or  '.BMP' in file:
                files.append(os.path.join(r ,file))
    label_state.configure(text="The folders are set. Press Next...")  # show on the GUI screen

def run_move():
    global current_file_index,current_file, inner_counter, moved
    moved=moved+1
    text = "{}".format(moved)
    label_moved.configure(text=text)  # show on the GUI screen
    infile = os.path.basename(current_file)
    for folder in folders:
        filename1=os.path.join(os.path.join(base_dir , folder) ,infile)
        filename2=os.path.join(out_dir , folder)
        print("{} >>> {} -> {}".format(moved, filename1, filename2))
        shutil.move(filename1, filename2)   # move file to another folder



def run_next():
    global current_file_index,current_file, inner_counter, timeout
    order=0
    if current_file_index<len(files):
        current_file=files[current_file_index]
        entry_current.delete(0, END)
        entry_current.insert(0, current_file)
        current_file_index=current_file_index+1
        inner_counter=0
        entry_skip.delete(0, END)
        entry_skip.insert(0, str(current_file_index))

        text = "#{}: {}".format(current_file_index,current_file)
        label_state.configure(text=text)  # show on the GUI screen
        title="The current image"

        img = cv2.imread(current_file)
        if not isinstance(img, np.ndarray): #empty
            print("Not ndarray, empty image!")
            return
        bar_pos = 0
        if chk_fit_big.get():
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)  # ,cv2.WINDOW_KEEPRATIO) #fit to window size
        else:
            cv2.namedWindow(title)  # show as is, even when big
        cv2.imshow(title, img)
        key= cv2.waitKey(timeout) & 0xFF   # wait for key press or for timeout
        cv2.destroyAllWindows()
        if key == ord("y") or key == 13 :  # enter key
            run_move()


    else:
        entry_current.delete(0, END)
        entry_current.insert(0, "")
        label_state.configure(text="No more files.")  # show on the GUI screen

def run_back():
    global current_file_index
    if current_file_index>0:
        current_file_index = current_file_index - 1

def run_skip():
    global current_file_index
    current_file_index=current_file_index+int(entry_skip.get())  #
    print("Current index skip to: {}\n".format(current_file_index))



button_init = Button(window, text="Init ", bg="orange", fg="black", command=load_folders)
button_init.grid(column=2, row=2)

button_init5 = Button(window, text="Skip", bg="orange", fg="blue", command=run_skip)
button_init5.grid(column=0, row=3)

label_3 = Label(window, anchor=E, text="-")
label_3.grid(column=0, row=4)   # widget's location

button_init3 = Button(window, text="Next", bg="orange", fg="blue", command=run_next)
button_init3.grid(column=2, row=5)

button_init4 = Button(window, text="Move", bg="orange", fg="blue", command=run_move)
button_init4.grid(column=4, row=5)

button_init4 = Button(window, text="One Back", bg="orange", fg="blue", command=run_back)
button_init4.grid(column=0, row=6)


window.mainloop()   #run the window loop

#termination

sys.exit(0)
