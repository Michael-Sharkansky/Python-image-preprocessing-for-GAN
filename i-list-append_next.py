#append couples or several of consecutive image files from a folder into one image file with scaling and fitting. For GAN model data.  The current version, any OS.
# like: image1, image2 -> \result\image1_d
#       image3, image4 -> \result\image3_d
# The folder of the input image MUST NOT contain any subfolders before the run !!!!
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
ap.add_argument("-i", "--path", required=False, help="Path to the images folder: --path <folder>")
args = vars(ap.parse_args())
print(args["path"])


#init global variables  ------------------------------------------------------------------------------------------
print(os.getcwd(), flush=True)  # print working dir (import os)
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)
stamp_start=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

final_size=256          #final size of cropped and resized to square image
save_as = ".jpg"        #to save as jpg (or png)
results_dir_f=""    #feature folder
base_dir=""
if args["path"] is not None:
    base_dir=args.get("path","")
    results_dir_f = base_dir
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
type=""
counter=0

# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Append couples or n-tuples of consecutive image files in the folder into one image.")
window.geometry('950x250')  # window size
# screen size
wss  =window.winfo_screenwidth()
hss = window.winfo_screenheight()
chk_debug=BooleanVar()     # fit big image to window, good when selectinf feature/label, can changed at any time
chk_debug.set(False)
chk_box_debug = Checkbutton(window, text="Show images", var=chk_debug)
chk_box_debug.grid(column=0, row=0)

chk_resize=BooleanVar()     # resize/scale the cropped image to the preset size (not togeher with tosize)
chk_resize.set(False)
chk_box_resize = Checkbutton(window, text="Auto Resize", var=chk_resize)
chk_box_resize.grid(column=2, row=0)

label_10 = Label(window, anchor=E, text="Q-ty files to append:")
label_10.grid(column=0, row=3)   #

entry_n = Entry(window, width=2)  # scale
entry_n.grid(column=1, row=3)  #
entry_n.insert(0, "2")

label_state = Label(window, text="Waiting for init.")
label_state.grid(column=6, row=3)

label_state1 = Label(window, text=" ")  # dummy to keep the line
label_state1.grid(column=6, row=4)

label_10 = Label(window, anchor=E, text="Orientation:")
label_10.grid(column=0, row=5)   # widget's location

combo_order = Combobox(window, width=11)
combo_order['values'] = ("Horizontally",  "Vertically", "Long", "Short" )      # append axis
combo_order.current(0)  # set the selected item
combo_order.grid(column=2, row=5)

label_11 = Label(window, anchor=E, text="Scale:")
label_11.grid(column=3, row=5)   # widget's location

entry_scale = Entry(window, width=5)  # scale
entry_scale.grid(column=4, row=5)  #
entry_scale.insert(0, "1.0")

label_1 = Label(window, anchor=E, text="Action:")
label_1.grid(column=0, row=11)   # widget's location

entry_ext = Entry(window, width=8)  # addition to the file name for this set of files
entry_ext.grid(column=0, row=4)  # location within the window
entry_ext.insert(0, "_d")


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

def scale_image2(img1, img2):	# scale the image 1 to the size of image2
    width=int(img2.shape[1] )
    height=int(img2.shape[0] )
    img1=cv2.resize(img1, (width, height), interpolation = cv2.INTER_LINEAR) # dft: INTER_LINEAR . INTER_NEAREST  INTER_CUBIC  INTER_LANCZOS4
    return img1

def rotateImage(image, angle):  #rotate image to an angle (positive - counterclockwise)
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags= cv2.INTER_LINEAR)     #dft: cv2.INTER_LINEAR
    return result


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

#=========================================================================================================
#take cropped feature and label files and append them verically of horizontally to make one image with two parts
def prepare_append2(file1, file2, file_out, axis):
    global results_dir_out, base_dir, counter

    # axis :       # 0- vertically, 1 - horizontally
    counter=counter+1
    print("1) ", file1," ", counter)
    print("2) ", file2," ", counter)
    img1 = cv2.imread(file1)
    img2 = cv2.imread(file2)
    fix=""
    #shape  [1]    [0]      [2]
    #      width  heigth   colors

    if axis == -1:  # automatic concatenate along the long side of the image
        if img1.shape[0] >= img1.shape[1]:      # heigth > width
            axis = 1
        else:                                   # width > heigth
            axis = 0
    elif axis == -2:  # automatic concatenate along the short side of the image
        if img1.shape[0] >= img1.shape[1]:      # heigth > width
            axis = 0
        else:                                   # width > heigth
            axis = 1

    if chk_resize.get():    #correct sizes that do not fit
        if img1.shape[0] == img2.shape[1] or img1.shape[1] == img2.shape[0]:  # the axises are swapped in images like 500X1000 and 1000X500
            print("Rotate ", file1)
            img2=np.swapaxes(img2,0,1)  # swap axes 0 and 1 of the shape[], i.e. rotate 90 degrees
            fix="_r"
        elif ((img1.shape[0] == img2.shape[0] and img1.shape[1]!=img2.shape[1] and axis==0 ) or # one axis is different like 1000X1000 and 1000X1024
            (img1.shape[0]!=img2.shape[0] and img1.shape[1]==img2.shape[1] and axis==1)):
            print("Resize ", file1)
            fix="_s"
            if img1.shape[0]*img1.shape[1] < img2.shape[0]*img2.shape[1]:
                img1=scale_image2(img1,img2)
            else:
                img2 = scale_image2(img2, img1)
        elif (img1.shape[0] != img2.shape[0] and img1.shape[1]!=img2.shape[1] ):  # both axis are different like 1200X1000 and 1100X1024
            print("Reformat ", file1)
            img1=scale_image2(img1, img2)
            fix="_f"

    # prepare output file name
    infile = os.path.basename(file2)
    root , ext= os.path.splitext(infile)
    root=root.replace('.','_',4)    # remove any dot from the filename
    file_out_ = os.path.join(results_dir_out,root+ entry_ext.get()+fix+".jpg")

    vis = np.concatenate((img1, img2), axis=axis)   # 0- vertically, 1 - horizontally
    vis=scale_image(vis) # scale if requested
    cv2.imwrite(file_out_, vis)
    print("Done ---- ", counter)

#=========================================================================================================

#=========================================================================================================
#take N files and append them verically of horizontally to make one image
def prepare_append_list(the_list, file_out, axis):
    global results_dir_out, base_dir

    # axis :       # 0- vertically, 1 - horizontally
    #shape  [1]    [0]      [2]
    #      width  heigth   colors

    fcount=0
    for a_file in the_list:
        if fcount==0:
            img1 = cv2.imread(a_file)
            vis=img1
            # prepare output file name
            infile = os.path.basename(a_file)
            root, ext = os.path.splitext(infile)
            root = root.replace('.', '_', 4)  # remove any dot from the filename
            file_out_ = os.path.join(results_dir_out, root + entry_ext.get() + ".jpg")
        else:
            img2 = cv2.imread(a_file)
            vis = np.concatenate((vis, img2), axis=axis)   # 0- vertically, 1 - horizontally
        print(fcount," ", a_file)
        fcount=fcount+1
    if fcount>0:    #there are files to be written
        vis=scale_image(vis) # scale if requested
        cv2.imwrite(file_out_, vis)
#=========================================================================================================


def run_loading() :
    global results_dir_f, files, base_dir
    global log_file, log_file_name
    global results_dir_out, scale_factor
    
    scale_factor=float(entry_scale.get()) 

    results_dir_f = filedialog.askdirectory(title="Folder of the input Images")
    base_dir = filedialog.askdirectory(title="Folder to contain Result Folder")
    if base_dir=="":    # if Cancel is pressed, set input folder as the default
        base_dir=results_dir_f

    print("Folders: {}  ".format(results_dir_f, ), flush=True)

    # r=root, d=directories, f = files
    for r, d, f in os.walk(results_dir_f):      # d and f are list, r is string
        for file in f:
            if '.jpg' or '.JPG' in file:
                files.append(os.path.join(r, file))

    label_state.configure(text="Folders are selected. Press Append.")  # show on the GUI screen
#=========================================================================================================



def run_add():
    global inner_counter
    global final_size
    global refPt, cropping, img, close_window
    global last_img_f , last_img_v
    global results_dir_out, base_dir
    count=0
    qty_n=int(entry_n.get())  # couple or n-tuple


    axis=0
    selected = combo_order.get()
    if selected == "Vertically":
        axis = 0  # 0- vertically, 1 - horizontally
        type="v"
    if selected == "Horizontally":
        axis = 1  # 0- vertically, 1 - horizontally
        type = "h"
    if selected == "Long":
        axis = -1  # 0- vertically, 1 - horizontally, here - along the long dimension
        type = "l"
    if selected == "Short":
        axis = -2  # 0- vertically, 1 - horizontally, here - along the short dimension
        type="s"

    stamp_h = "{:02d}{:02d}".format(datetime.now().hour, datetime.now().minute)
    stamp_d = "{:02d}{:02d}{:02d}_".format(datetime.now().year%100,datetime.now().month, datetime.now().day)+stamp_h+type
    if base_dir != "":
        results_dir_out=os.path.join(base_dir,stamp_d)	# result output folder  ....
        if os.path.exists(results_dir_out):
            results_dir_out = os.path.join(results_dir_out, "_n")  # increment result output folder  ....
        os.mkdir(results_dir_out)

    filename1=""
    filename2=""
    files_app = []  # list of n-tuples
    file_o=""
    int_count=0  # counter for list of n-tuples
    for  filename in files:  #get input file from gui
        #img1 = cv2.imread(filename)
        if count % qty_n == 0 :          #  <<<<
            filename1=filename
            files_app.clear()
            files_app.append(filename)  # <<<
            int_count=int_count+1
        else:
            filename2=filename
            infile = os.path.basename(filename)
            root , ext= os.path.splitext(infile)
            root=root.replace('.','_',4)    # remove any dot from the filename
            file_o = os.path.join(results_dir_out,root+ entry_ext.get()+".jpg")
            files_app.append(filename)      # <<<<<<
            int_count=int_count+1
            if int_count == qty_n and qty_n==2 :    # to append couples
                prepare_append2(filename1, filename2, file_o, axis)
                int_count = 0
            elif int_count == qty_n and qty_n>2 :  # to append n-tuples
                prepare_append_list(files_app, file_o, axis)
                int_count = 0
        count=count+1


    label_state.configure(text="No more files.")  # show on the GUI screen

#======================================================================================

def on_change():
    return

button_init = Button(window, text="Initialize\nfor Append ", bg="orange", fg="black", command=run_loading)
button_init.grid(column=2, row=3)

button_init1 = Button(window, text="Append", bg="orange", fg="red", command=run_add)
button_init1.grid(column=2, row=12)

window.mainloop()   #run the window loop

#termination
stamp=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

print("END: from {} to {}. ".format(stamp_start, stamp), flush=True)
sys.exit(0)
#===============================================================================================================================

