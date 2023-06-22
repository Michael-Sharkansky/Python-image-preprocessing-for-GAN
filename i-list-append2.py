#append sequence of images into couples of small sniplets with scaling. For GAN model data.  The current version, any OS.
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
args = vars(ap.parse_args())
print(args["path"])


#init global variables  ------------------------------------------------------------------------------------------
print(os.getcwd(), flush=True)  # print working dir (import os)
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)
stamp_start=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

final_size=256          #final size of cropped and resized to square image
save_as = ".jpg"        #to save as jpg (or png)
base_dir=""
if args["path"] is not None:
    base_dir=args.get("path","")
results_dir_f=""    #feature folder
results_dir_l=""    #label folder
results_dir_fl=""    #feature+label folder
current_file_index=0
current_file=""
files = []
inner_counter=0
img=None
log_file_name=""
log_file=None
title="The image"
last_img_f=""
last_img_v=""
results_dir_out=""
order=0
size_1sti = .5
scale_factor = 1.0


# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Append couples of image files from 2 folders or Split appended images into separate files")
window.geometry('950x250')  # window size

chk_debug=BooleanVar()     # fit big image to window, good when selectinf feature/label, can changed at any time
chk_debug.set(False)
chk_box_debug = Checkbutton(window, text="Show images", var=chk_debug)
chk_box_debug.grid(column=0, row=0)

label_10 = Label(window, anchor=E, text="Orientation:")
label_10.grid(column=0, row=4)   # widget's location

combo_order = Combobox(window, width=11)
combo_order['values'] = ("Horizontally",  "Vertically" )      # append axis
combo_order.current(0)  # set the selected item
combo_order.grid(column=2, row=4)

label_11 = Label(window, anchor=E, text="Scale:")
label_11.grid(column=3, row=4)   # widget's location

entry_scale = Entry(window, width=5)  # scale
entry_scale.grid(column=4, row=4)  # 
entry_scale.insert(0, "1.0")

label_state = Label(window, text="Waiting for init.")
label_state.grid(column=6, row=17)

chk_auto=BooleanVar()     # fit big image to window, good when selectinf feature/label, can changed at any time
chk_auto.set(False)
chk_box_auto = Checkbutton(window, text="Automatic\norientation", var=chk_auto)
chk_box_auto.grid(column=0, row=18)

one_part="1 Part of"
combo_type = Combobox(window, width=8)
combo_type['values'] = (one_part,  "Pixels")
combo_type.current(0)  # set the selected item
combo_type.grid(column=2, row=19)

label_1 = Label(window, text="For the 1st part:")
label_1.grid(column=0, row=19)

entry_1st = Entry(window, width=6)  # it is eithe denominator of the part of the picture: 2, 3, 4, or size of it in pixels: 256, 512 etc.
entry_1st.grid(column=3, row=19)  #
entry_1st.insert(0, "0")


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

# split image into 2 halves, verically of horizontally
def prepare_split(filename, filename1, filename2):
    global size_1sti

    debug=chk_debug.get()
    vertical=False
    image = cv2.imread(filename)
    height, width = image.shape[:2]
    if chk_auto.get():
        if height>width:
            vertical = True
        else :
            vertical=False
    else:
        selected = combo_order.get()
        if selected == "Vertically":
            vertical = True
        if selected == "Horizontally":
            vertical=False

    # Let's get the starting pixel coordiantes (top left of cropped top)
    start_row, start_col = int(0), int(0)
    # Let's get the ending pixel coordinates (bottom right of cropped top)
    if combo_type.get() == one_part:
        if vertical:
            end_row, end_col = int(height * size_1sti), int(width)
        else:
            end_row, end_col = int(height), int(width * size_1sti)
    elif combo_type.get()=="Pixels":
        if vertical:
            end_row, end_col = int(size_1sti), int(width)
        else:
            end_row, end_col = int(height), int(size_1sti)

    cropped_top = image[start_row:end_row , start_col:end_col]
    cropped_top=scale_image(cropped_top)
    cv2.imwrite(filename1, cropped_top)

    if debug:
        cv2.imshow("Cropped Top", cropped_top)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Let's get the starting pixel coordiantes (top left of cropped bottom)
    if vertical:
        start_row, start_col = int(height * .5), int(0)
    else:
        start_row, start_col = int(), int(width * .5)

    # Let's get the ending pixel coordinates (bottom right of cropped bottom)
    end_row, end_col = int(height), int(width)
    cropped_bot = image[start_row:end_row , start_col:end_col]
    cropped_bot=scale_image(cropped_bot)
    cv2.imwrite(filename2, cropped_bot)

    if debug:
        cv2.imshow("Cropped Bot", cropped_bot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
#=========================================================================================================

def run_split() :
    global results_dir_f, results_dir_l, results_dir_fl,  files, base_dir
    global log_file, log_file_name
    global results_dir_out
    global size_1sti

    size_1st=entry_1st.get()
    if size_1st!='0':
        if combo_type.get()==one_part:
            size_1sti=1/int(size_1st)
            print("1st part ratio=",size_1sti)
        elif combo_type.get()=="Pixels":
            size_1sti=size_1st
            print("1st part ratio=",size_1sti)
        else:
            return

    count=0

    base_dir = filedialog.askdirectory(title="Folder to contain original images")

    results_dir_f = filedialog.askdirectory(title="Folder of splitted Features")
    results_dir_l = filedialog.askdirectory(title="Folder of splitted Labels")
    print("Folders: {} and {}. ".format(results_dir_f, results_dir_l), flush=True)

    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for file in f:
            if '.jpg' or '.JPG' in file:
                files.append(os.path.join(r, file))

    label_state.configure(text="Folders are selected.")  # show on the GUI screen
    for  filename in files:  #get input file from gui
        count=count+1
        infile=os.path.basename(filename)
        #img1 = cv2.imread(filename)

        filename1=os.path.join(results_dir_f, infile)
        filename2=os.path.join(results_dir_l, infile)
        prepare_split(filename, filename1, filename2, )

    label_state.configure(text="No more files.")  # show on the GUI screen

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


def run_loading() :
    global results_dir_f, results_dir_l, results_dir_fl,  files, base_dir
    global log_file, log_file_name
    global results_dir_out, scale_factor
    
    scale_factor=float(entry_scale.get()) 

    base_dir = filedialog.askdirectory(title="Folder to contain Result Folder")

    results_dir_f = filedialog.askdirectory(title="Folder of Features")
    results_dir_l = filedialog.askdirectory(title="Folder of Labels")
    print("Folders: {} and {}. ".format(results_dir_f, results_dir_l), flush=True)

    # r=root, d=directories, f = files
    for r, d, f in os.walk(results_dir_f):
        for file in f:
            if '.jpg' or '.JPG' in file:
                files.append(os.path.join(r, file))

    label_state.configure(text="Folders are selected. Press Append.")  # show on the GUI screen
#=========================================================================================================


def run_loading_more():  # set output folder to be feature folder, get another label folder and make new output folder, base-dir stays the same
    global results_dir_f, results_dir_l, results_dir_fl,  files, base_dir
    global log_file, log_file_name
    global results_dir_out

    # base_dir = filedialog.askdirectory(title="Folder to contain Result Folder")  stays the same

    results_dir_f = results_dir_out    # (title="Folder of Features")
    results_dir_l = filedialog.askdirectory(title="Folder of Labels")
    print("Folders: {} and {}. ".format(results_dir_f, results_dir_l), flush=True)
    del files[:]   # clear the files list

    # r=root, d=directories, f = files
    for r, d, f in os.walk(results_dir_f):
        for file in f:
            if '.jpg' or '.JPG' in file:
                files.append(os.path.join(r, file))

    label_state.configure(text="Folders are selected. Wait 1 min and press Append.")  # show on the GUI screen
    # the new output folder will be created and filled upon pressing Append button.


def run_add():
    global inner_counter
    global final_size
    global refPt, cropping, img, close_window
    global last_img_f , last_img_v
    global results_dir_out
    count=0

    stamp_h = "{:02d}{:02d}".format(datetime.now().hour, datetime.now().minute)
    stamp_d = "{:02d}{:02d}{:02d}_".format(datetime.now().year%100,datetime.now().month, datetime.now().day)+stamp_h
    if base_dir != "":
        results_dir_out=os.path.join(base_dir,stamp_d+"fl")	# result output folder  ....fl
        if os.path.exists(results_dir_out):
            results_dir_out = os.path.join(results_dir_out, "_n")  # increment result output folder  ....fl
        os.mkdir(results_dir_out)

    axis=0
    selected = combo_order.get()
    if selected == "Vertically":
        axis = 0  # 0- vertically, 1 - horizontally
    if selected == "Horizontally":
        axis = 1  # 0- vertically, 1 - horizontally

    for  filename in files:  #get input file from gui
        count=count+1
        infile=os.path.basename(filename)
        #img1 = cv2.imread(filename)

        filename2=os.path.join(results_dir_l, infile)
        if  os.path.exists(filename2):
            print(count," <<<", infile)
            #img2 = cv2.imread(filename2)
            file_o = os.path.join(results_dir_out,infile)
            prepare_append2(filename, filename2, file_o, axis)
        else:
            print(count, " skip: ",infile)

    label_state.configure(text="No more files.")  # show on the GUI screen

#======================================================================================

def on_change():
    return

button_init = Button(window, text="Initialize\nfor Append ", bg="orange", fg="black", command=run_loading)
button_init.grid(column=2, row=3)

button_init = Button(window, text="Set to Append\nanother folder", bg="orange", fg="black", command=run_loading_more)
button_init.grid(column=4, row=3)

label_1 = Label(window, anchor=E, text="Action:")
label_1.grid(column=0, row=11)   # widget's location

button_init1 = Button(window, text="Append", bg="orange", fg="red", command=run_add)
button_init1.grid(column=2, row=12)

button_inits = Button(window, text="Split", bg="orange", fg="red", command=run_split)
button_inits.grid(column=2, row=18)

window.mainloop()   #run the window loop

#termination
stamp=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

print("END: from {} to {}. ".format(stamp_start, stamp), flush=True)
sys.exit(0)
#===============================================================================================================================

