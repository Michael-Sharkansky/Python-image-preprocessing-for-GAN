#append sequence of images into line of small sniplets with scaling. For GAN model data.  The current version, any OS.
#Programmed by Michael Sharkansky

import os
import argparse
import subprocess
import time
from datetime import datetime
import numpy as np
import io
import cv2  # use: pip install opencv-contrib-python
# import winsound

#GUI with tkinter, see https://likegeeks.com/python-gui-examples-tkinter-tutorial/
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog

# construct the argument parser and parse the arguments --------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--path", required=False, help="Path to the images folder")
ap.add_argument("-c", "--conf", required=False, help="Path to the configuration file")
args = vars(ap.parse_args())
print(args["path"])
print("Base: ",args["path"])
print("Conf: ",args["conf"])


#init global variables  ------------------------------------------------------------------------------------------
print(os.getcwd(), flush=True)  # print working dir (import os)
work_path=os.path.dirname(os.path.realpath(__file__))
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)
stamp_start=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

base_dir=""
if args["path"] is not None:
    base_dir=args.get("path","")
results_dir_f=""    #feature folder
results_dir_l=""    #label folder
results_dir_fl=""    #feature+label folder
files = []
img=None
title="The image"
results_dir_out=""
order=0
scale_factor = 1.0
folder_list=[]
folder_list_count=0
config_loaded=False
if args["conf"] is not None:
    config=args.get("conf","")
else:
    config = os.path.join(work_path, "conf_append_n.txt")

# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Append image files from a list of folders in conf_append_n.txt")
window.geometry('950x250')  # window size

chk_debug=BooleanVar()     # fit big image to window, good when selectinf feature/label, can changed at any time
chk_debug.set(False)
chk_box_debug = Checkbutton(window, text="Show images", var=chk_debug)
chk_box_debug.grid(column=0, row=0)

label_x = Label(window, text=" ")
label_x.grid(column=2, row=4)

label_10 = Label(window, anchor=E, text="Orientation:")
label_10.grid(column=0, row=5)   # widget's location

combo_order = Combobox(window, width=11)
combo_order['values'] = ("Horizontally",  "Vertically" )      # append axis
combo_order.current(0)  # set the selected item
combo_order.grid(column=2, row=5)

label_11 = Label(window, anchor=E, text="Scale:")
label_11.grid(column=3, row=5)   # widget's location

entry_scale = Entry(window, width=5)  # scale
entry_scale.grid(column=4, row=5)  #
entry_scale.insert(0, "1.0")

label_state = Label(window, text="Waiting to select the configuration file or to load the default one (conf_append_n.txt).")
label_state.grid(column=6, row=17)

#--------------------------------------------------------------------------------------------


# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
close_window=False

def scale_image(img):	# scale the image for output
    if scale_factor!=1.0:
        width=int(img.shape[1] * scale_factor)
        height=int(img.shape[0] * scale_factor)
        img=cv2.resize(img, (width, height), interpolation = cv2.INTER_LINEAR) # dft: INTER_LINEAR . INTER_NEAREST  INTER_CUBIC  INTER_LANCZOS4
    return img

#mouse event callback,
# see https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/
def  click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping, img, close_window

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True
    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        # draw a rectangle around the region of interest
        cv2.rectangle(img, refPt[0], refPt[1], (0, 255, 0), 2)  #green line of width 2
        cv2.imshow(title, img)
    if event == cv2.EVENT_RBUTTONUP:
        close_window=True
#=========================================================================================================

def get_action(title,img):
    # keep looping until the 'q' key is pressed
    action=True
    while True:
        # display the image and wait for a keypress
        cv2.imshow(title, img)
        key = cv2.waitKey(1) & 0xFF
        # print(key)
        # if the 'r' or Esc key is pressed, reset the cropping region
        if key == ord("r") or key == 27:
            action=False
            break
        # if the 'c' or space key is pressed, break from the loop
        elif key == ord("c") or key == ord(" "):
            break
    return action

def rotateImage(image, angle):  #roteate image to an angle (positive - counterclockwise)
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result
#=========================================================================================================



#take cropped feature and label files and append them verically of horizontally to make one image with two parts
def prepare_append2(file1, file2, file_out, axis):
    # axis :       # 0- vertically, 1 - horizontally
    img1 = cv2.imread(file1)
    img2 = cv2.imread(file2)
    vis = np.concatenate((img1, img2), axis=axis)   # 0- vertically, 1 - horizontally
    vis=scale_image(vis) # scale if requested
    cv2.imwrite(file_out, vis)
#=========================================================================================================


def select_config():
    global config, config_loaded
    config = filedialog.askopenfilename(title="Select the config file") # .askdirectory(title="Folder with config file")
    print("Config: {} . ".format(config), flush=True)
    config_loaded=False
    label_state.configure(text="Waiting to load the selected configuration file.")  # show on the GUI screen



def get_config_line(in_parms): # read next line that is not comment
    while True:
        lin1=in_parms.readline()[:-1]
        if (len(lin1) == 0 or lin1[0]!='#'):
            break
    return lin1

def run_loading_list():
    global results_dir_f, results_dir_l, results_dir_fl, files, base_dir
    global results_dir_out, folder_list, folder_list_count, config, config_loaded
    print("Use Config: {} . ".format(config), flush=True)

    folder_list_count=0
    folder_list=[]
    if os.path.isfile(config):
        in_config = open(config, 'rt')
        config_loaded=True
        while True:
            dir_win = get_config_line(in_config)  # path for data
            if dir_win=="" :
                break
            folder_list_count=folder_list_count+1
            if folder_list_count==1:    # Folder to contain Result Folder  - base_dir
                base_dir=dir_win
                print("Base Folder: {}.".format(dir_win), flush=True)
            elif folder_list_count==2:  # Folder of Features - leading - results_dir_f
                results_dir_f=dir_win
                print("Leading Folder: {}.".format(dir_win), flush=True)
            else:
                folder_list.append(dir_win)  #  other folders (labels) to append - results_dir_l
                print("Folder: {}.".format(dir_win), flush=True)
    else:
        print("File {} not found in {} ".format(config, os.getcwd()), flush=True)
        return

    # r=root, d=directories, f = files
    for r, d, f in os.walk(results_dir_f):
        for file in f:
            if '.jpg' or '.JPG' in file:
                files.append(os.path.join(r, file))

    label_state.configure(text="Folders are selected. Press Append.")  # show on the GUI screen
# =========================================================================================================


def run_add():
    global refPt, cropping, img, close_window, scale_factor
    global results_dir_out, config, config_loaded
    count=0
    if (not config_loaded):
        return


    stamp_h = "{:02d}{:02d}".format(datetime.now().hour, datetime.now().minute)
    stamp_d = "{:02d}{:02d}{:02d}_".format(datetime.now().year %100,  datetime.now().month, datetime.now().day)+stamp_h
    if base_dir != "":
        results_dir_out=os.path.join(base_dir,stamp_d+"fl")	# result output folder  ....fl
        if os.path.exists(results_dir_out):
            results_dir_out = os.path.join(results_dir_out, "_n")  # increment result output folder  ....fl
        os.mkdir(results_dir_out)
    print("Output Folder: {}.".format(results_dir_out), flush=True)

    scale_factor = float(entry_scale.get())
    axis=0
    selected = combo_order.get()
    if selected == "Vertically":
        axis = 0  # 0- vertically, 1 - horizontally
    if selected == "Horizontally":
        axis = 1  # 0- vertically, 1 - horizontally

    for  filename in files:  #get input file from gui
        count=count+1
        infile=os.path.basename(filename)
        img1 = cv2.imread(filename)
        file_o = os.path.join(results_dir_out, infile)
        print(count, " ===", filename)

        for results_dir_l in folder_list:
            filename2=os.path.join(results_dir_l, infile)
            if  os.path.exists(filename2):
                print(count," <<<", filename2)
                img2 = cv2.imread(filename2)
                # take cropped feature and label files and append them verically of horizontally to make one image with two parts
                # axis :       # 0- vertically, 1 - horizontally
                vis = np.concatenate((img1, img2), axis=axis)  # 0- vertically, 1 - horizontally
                img1=vis
                #prepare_append2(filename, filename2, file_o, axis)
            else:
                print(count, " skip: ",infile)
        img1 = scale_image(img1)  # scale if requested
        cv2.imwrite(file_o, img1)

    label_state.configure(text="No more files.")  # show on the GUI screen

#======================================================================================

button_init = Button(window, text="Load Config file", bg="orange", fg="black", command=run_loading_list)
button_init.grid(column=4, row=3)

button_init = Button(window, text="Select Config file", bg="orange", fg="black", command=select_config)
button_init.grid(column=2, row=3)

label_1 = Label(window, anchor=E, text="Action:")
label_1.grid(column=0, row=11)   # widget's location

button_init1 = Button(window, text="Append", bg="orange", fg="red", command=run_add)
button_init1.grid(column=2, row=12)

window.mainloop()   #run the window loop

#termination
stamp=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

print("END: from {} to {}. ".format(stamp_start, stamp), flush=True)
sys.exit(0)
#===============================================================================================================================

