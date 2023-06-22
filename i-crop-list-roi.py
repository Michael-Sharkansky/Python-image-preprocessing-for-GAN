#crop and resize sequence of images into couples of small sniplets or into single ROI sniplets. The current version, any OS.
#includes moving into other folders by up to 5 categories.
#Use left button to select region
#Use middle button to draw axis that will be the vertical one after image rotation.
#Programmed by Michael Sharkansky

import os
import argparse
import subprocess
import time
from datetime import datetime
import numpy as np
import io
import shutil
import glob
import cv2  # use: pip install opencv-contrib-python
#import winsound
import platform
import math

#GUI with tkinter, see https://likegeeks.com/python-gui-examples-tkinter-tutorial/
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog

# construct the argument parser and parse the arguments --------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--path", required=False, help="Path to the images folder")
ap.add_argument("-c", "--conf", required=False, help="Path to the configuration file")
args = vars(ap.parse_args())
print("Base: ",args["path"])
print("Conf: ",args["conf"])
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)


#init global variables  ------------------------------------------------------------------------------------------
print(os.getcwd(), flush=True)  # print working dir (import os)
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)
stamp_start=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

p_system=platform.system()
final_size=256          #final size of cropped and resized to square image
save_as = ".jpg"        #to save produced images as jpg (or png)
base_dir=""
if args["path"] is not None:
    base_dir=args.get("path","")
results_dir_f=""    #feature folder
results_dir_l=""    #label folder
results_dir_fl=""    #feature+label folder
result_dirs=""
first_dir=""      # not used
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
file_f=""
type_name={ "F" : "Feature", "L" : "Label", "X" : "Full image"}
done=0


out_dir1=""
out_dir2=""
out_dir3=""
out_dir4=""
out_dir5=""
last_dir=""
config=""

if p_system=="windows" or p_system=="Windows":
    init_move_to_dir="C:/Temp"  # for Move To
else:
    init_move_to_dir="/media/dextr/581D5BDF7864CD5C/Temp"

def get_config_line(in_parms): # read next line that is not comment
    while True:
        lin1=in_parms.readline()[:-1]
        if (len(lin1) == 0 or lin1[0]!='#'):
            break
    return lin1


if args["conf"] is not None:    # load config file with folder names
    config=args.get("conf","")
    if not os.path.isfile(config):
        config=os.path.join(os.path.dirname(os.path.realpath(__file__)), config)
    print("Loading config: ",config)
    if os.path.isfile(config):
        in_conf = open(config, 'rt')
        base_dir=get_config_line(in_conf)   # base folder
        first_dir=get_config_line(in_conf)  # leading sub-folder (not in use here)
        out_dir1=get_config_line(in_conf)   # cathegory folder 1
        out_dir2=get_config_line(in_conf)   # cat folder 2
        out_dir3=get_config_line(in_conf)   # cat folder 3
        out_dir4=get_config_line(in_conf)   # cat folder 4
        out_dir5=get_config_line(in_conf)   # cat folder 5
        in_conf.close()
        print("Loaded. Press the Config button to set the data from the folders.")
    else:
        config=""


# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Crop, resize, rotate (v2.1)")
window.geometry('1010x630')  # window size

label_ifile = Label(window, anchor=E, text="Current file:")
label_ifile.grid(column=5, row=0)   # widget's location

entry_current = Entry(window, width=90)  # THE FILE NAME INPUT widget
entry_current.grid(column=6, row=0)  # location within the window
entry_current.insert(0, "?")

label_class = Label(window, anchor=E, text="Class:")
label_class.grid(column=1, row=0)   # widget's location

entry_class = Entry(window, width=10)  # class type to be added to output file names, like _good, _bad, for the 'not same name' option
entry_class.grid(column=2, row=0)  # location within the window
entry_class.insert(0, "")

entry_skip = Entry(window, width=8)  # skip files  widget
entry_skip.grid(column=1, row=1)  # location within the window
entry_skip.insert(0, "0")

label_done = Label(window, anchor=E, text="0")
label_done.grid(column=1, row=15)   # widget's location

combo_inter = Combobox(window, width=16, state='readonly')
combo_inter['values'] = ("INTER_LINEAR",  "INTER_AREA",  "INTER_NEAREST", "INTER_CUBIC", "INTER_LANCZOS4", "DEFAULT" )      # resize interpolation
combo_inter.current(0)  # set the selected item
combo_inter.grid(column=6, row=3)


chk_resize=BooleanVar()     # resize/scale the cropped image to the preset size (not togeher with tosize)
chk_resize.set(True)
chk_box_resize = Checkbutton(window, text="Resize", var=chk_resize)
chk_box_resize.grid(column=6, row=9)

entry_resize = Entry(window, width=8)  # side size for resize
entry_resize.grid(column=6, row=10)  # location within the window
entry_resize.insert(0, str(final_size))

chk_square=BooleanVar()     #force cropped picture to be square of any size, unscaled (not togeher with tosize)
chk_square.set(True)
chk_box_square = Checkbutton(window, text="Force to square form", var=chk_square)
chk_box_square.grid(column=6, row=11)

chk_tosize=BooleanVar()     #force cropped picture to be square of preset size, when unscaled square of given size must be cropped
chk_tosize.set(False)
chk_box_tosize = Checkbutton(window, text="Force to this size", var=chk_tosize)
chk_box_tosize.grid(column=6, row=12)

chk_same_name=BooleanVar()    # keep same name of output images
chk_same_name.set(True)
chk_box_same_name = Checkbutton(window, text="Output to the same name", var=chk_same_name)
chk_box_same_name.grid(column=6, row=13)

chk_feature=BooleanVar()    # check order of features and labels
chk_feature.set(True)
chk_box_sfeature = Checkbutton(window, text="Features and Labels Order", var=chk_feature)
chk_box_sfeature.grid(column=6, row=14)

chk_append2=BooleanVar()    # append feature and label to one image
chk_append2.set(True)
chk_box_append2 = Checkbutton(window, text="Append 2 results", var=chk_append2)
chk_box_append2.grid(column=6, row=15)

chk_fit_big=BooleanVar()     # fit big image to window, good when selectinf feature/label, can changed at any time
chk_fit_big.set(False)
chk_box_fit_big = Checkbutton(window, text="Fit big\nimage", var=chk_fit_big)
chk_box_fit_big.grid(column=2, row=15)

chk_fit_big_keep=BooleanVar()     # fit big image to window, good when selectinf feature/label, can changed at any time
chk_fit_big_keep.set(False)
chk_box_fit_big_keep = Checkbutton(window, text="always", var=chk_fit_big_keep)
chk_box_fit_big_keep.grid(column=3, row=15)

label_bl1 = Label(window, anchor=E, text="-")
label_bl1.grid(column=0, row=2)   # widget's location

# set for the title bar of IrfanView region selection (x, y; w X h)
label_ifile = Label(window, anchor=E, text="X,Y,W,H")
label_ifile.grid(column=0, row=3)   # widget's location

entry_x = Entry(window, width=8)  # x
entry_x.grid(column=1, row=3)
entry_x.insert(0, str(0)) #put text into the entry widget:

entry_y = Entry(window, width=8)  # y
entry_y.grid(column=2, row=3)
entry_y.insert(0, str(0)) #put text into the entry widget:

entry_w = Entry(window, width=8)  # w
entry_w.grid(column=3, row=3)
entry_w.insert(0, str(0)) #put text into the entry widget:

entry_h = Entry(window, width=8)  # h
entry_h.grid(column=4, row=3)
entry_h.insert(0, str(0)) #put text into the entry widget:

chk_irfan=BooleanVar()
chk_irfan.set(False)
chk_box_irfan = Checkbutton(window, text="IrfanView", var=chk_irfan)
chk_box_irfan.grid(column=3, row=2)

chk_preview=BooleanVar()
chk_preview.set(True)
chk_box_preview = Checkbutton(window, text="Preview", var=chk_preview)
chk_box_preview.grid(column=4, row=2)

label_ifile3 = Label(window, anchor=E, text="Save as")
label_ifile3.grid(column=0, row=5)   # widget's location 1,5

entry_save_as = Entry(window, width=8)  # h
entry_save_as.grid(column=1, row=5)     # 2,5
entry_save_as.insert(0,  save_as) #put text into the entry widget: .jpg

entry_temp = Entry(window, width=40)  # y
entry_temp.grid(column=6, row=6)  # 1,10
entry_temp.insert(0, init_move_to_dir) #put text into the entry widget: temp folder to move files (Move To)

combo_move_all = Combobox(window, width=7, state='readonly')
combo_move_all['values'] = ("Sniplets",  "Source",   "All" )      # what to move: the image, the small picture or all
combo_move_all.current(0)  # set the selected item
combo_move_all.grid(column=4, row=6)   # 2,10

# rotation outliers fill
combo_outlier = Combobox(window, width=9, state='readonly')
combo_outlier['values'] = ("Constant",  "Transparent" )      # outlier of rotation (single color or previous background
combo_outlier.current(0)  # set the selected item
combo_outlier.grid(column=2, row=11)

entry_r = Entry(window, width=3)  # red
entry_r.grid(column=3, row=11)
entry_r.insert(0, str(0)) # 0 in all of colors for black

entry_g = Entry(window, width=3)  # green
entry_g.grid(column=4, row=11)
entry_g.insert(0, str(0)) # 0 default

entry_b = Entry(window, width=3)  # blue
entry_b.grid(column=5, row=11)
entry_b.insert(0, str(0)) #  0 dft

label_rot = Label(window, anchor=E, text="Rotate CCW\n+ <= -")
label_rot.grid(column=2, row=12)   # widget's location

entry_rot = Entry(window, width=5)  # counter-clockwise rotation angle
entry_rot.grid(column=2, row=13)
entry_rot.insert(0, '') #put text into the entry widget

label_rot1 = Label(window, anchor=E, text="Rotate CW\n =>")
label_rot1.grid(column=0, row=12)   # widget's location

entry_rot1 = Entry(window, width=5)  # clockwise rotation angle
entry_rot1.grid(column=0, row=13)
entry_rot1.insert(0, '') #put text into the entry widget

label_last = Label(window, text="*")
label_last.grid(column=1, row=13)

combo_order = Combobox(window, width=11)
combo_order['values'] = ("Horizontally",  "Vertically" )      # append axis
combo_order.current(1)  # set the selected item
combo_order.grid(column=6, row=16)


label_last_categ = Label(window, anchor=E, text=">")    # the last category that was selected
label_last_categ.grid(column=0, row=17)   

chk_fixed_folder=BooleanVar()   # if true, use fixed subfolder names: dataff, datall, datafl, otherwise use foder names with time stamps
chk_fixed_folder.set(True)
chk_box_fixed_folder = Checkbutton(window, text="Fixed sub-folder names", var=chk_fixed_folder)
chk_box_fixed_folder.grid(column=6, row=17)

chk_copy=BooleanVar()   # if true, move file, else copy them
chk_copy.set(True)
chk_box_copy = Checkbutton(window, text="Move", var=chk_copy)
chk_box_copy.grid(column=0, row=18)

chk_timeout=BooleanVar()   # if true, use fixed subfolder names: dataff, datall, datafl, otherwise use foder names with time stamps
chk_timeout.set(False)
chk_box_timeout = Checkbutton(window, text="Exit image on timeout", var=chk_timeout)
chk_box_timeout.grid(column=6, row=19)

label_state = Label(window, text="Waiting for init.")
label_state.grid(column=6, row=21)

#--------------------------------------------------------------------------------------------
def beep():
    frequency = 80  # Set Frequency To 800 Hertz
    duration = 500  # Set Duration To 1000 ms == 1 second
    #winsound.Beep(frequency, duration)


# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
verPt = []
cropping = False
align = False
abandon=False
proceed=False

def get_interplation():
    #"INTER_LINEAR", "INTER_NEAREST", "INTER_AREA", "INTER_CUBIC", "INTER_LANCZOS4"
    # INTER_NEAREST - a nearest-neighbor interpolation
    # INTER_LINEAR - a bilinear interpolation (used by default)
    # INTER_AREA - resampling using pixel area relation. It may be a preferred method for image decimation, as it gives moire’-free results.
    #               But when the image is zoomed, it is similar to the INTER_NEAREST method.
    # INTER_CUBIC - a bicubic interpolation over 4x4 pixel neighborhood
    # INTER_LANCZOS4 - a Lanczos interpolation over 8x8 pixel neighborhood

    selected = combo_inter.get()
    if selected == "INTER_LINEAR":
        return cv2.INTER_LINEAR
    elif selected == "INTER_NEAREST":
        return cv2.INTER_NEAREST
    elif selected == "INTER_AREA":
        return cv2.INTER_AREA
    elif selected == "INTER_CUBIC":
        return cv2.INTER_CUBIC
    elif selected == "INTER_LANCZOS4":
        return cv2.INTER_LANCZOS4
    else:
        return cv2.INTER_LINEAR


#mouse event callback,
# see https://www.pyimagesearch.com/2015/03/09/capturing-mouse-click-events-with-python-and-opencv/
def  click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping, img, abandon, title, verPt, align, proceed

    # With the middle button, draw a line that will become the vertical axis of the image after the rotation
    if event == cv2.EVENT_MBUTTONDOWN:  #start assumed vertical axis,  to rotate the image, click middle button
        verPt = [(x, y)]
        align = True
        cv2.drawMarker(img, verPt[0], (0, 155, 155))  # add small pale cross for the starting point of ROI (BGR)
    if event == cv2.EVENT_MBUTTONUP:    # end assumed vertical axis,  to rotate the image, release middle button
        verPt.append((x, y))
        # draw a line around the region of interest
        #cv2.line(img, verPt[0], verPt[1], (128, 128, 0), 2)  #magenta line of width 2
        cv2.arrowedLine(img, verPt[1], verPt[0], (128, 128, 0), 2)  #magenta arrow of width 2, tip looks up (color is BGR)
        align = False

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cv2.drawMarker(img, refPt[0], (0, 0, 255))  # add small red cross for the starting point of ROI (BGR)
        cropping = True
    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished, if it was initiated; thus it is distinguished from
        if cropping:
            refPt.append((x, y))
        cropping = False

        # draw a rectangle around the region of interest and write its size over the image
        text="{:03d}:{:03d}".format(refPt[1][0]-refPt[0][0], refPt[1][1]-refPt[0][1] )
        cv2.putText(img,text, (10,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 1)
        cv2.rectangle(img, refPt[0], refPt[1], (0, 255, 0), 2)  #green line of width 2
        cv2.imshow(title, img)
    if event == cv2.EVENT_RBUTTONUP:
        proceed = True
    #if event == cv2.EVENT_RBUTTONDBLCLK:        # EVENT_RBUTTONDBLCLK   EVENT_MBUTTONDBLCLK  EVENT_LBUTTONDBLCLK
    #    abandon=True

#=========================================================================================================


#def get_action(title_inp,img):
#    global refPt, verPt
#    # keep looping until the 'q' key is pressed
#    action=True
#    while True:
#        # display the image and wait for a keypress
#        cv2.imshow(title_inp, img)
#        key = cv2.waitKey(1) & 0xFF
#        # print(key)
#        # if the 'r' or Esc key is pressed, reset the cropping region
#        if key == ord("r") or key == 27:
#            action=False
#            refPt = []
#            verPt = []
#            break
#        # if the 'c' or space key is pressed, break from the loop
#        elif key == ord("c") or key == ord(" "):
#            break
#    return action

def rotateImage(image, angle):  #rotate image to an angle (positive - counterclockwise)
    selected = combo_outlier.get()  # set outliers area
    if selected=="Transparent":
        borderMode = cv2.BORDER_TRANSPARENT     # leave as it is, does not work good...
        b_r=0
        b_g=0
        b_b=0
        print("Transparent rotation")
    else:   # "Constant"
        borderMode = cv2.BORDER_CONSTANT    # fill with a color
        b_r=int(entry_r.get())
        if b_r<0 or b_r>255: b_r=0
        b_g=int(entry_g.get())
        if b_g<0 or b_g>255: b_g=0
        b_b=int(entry_b.get())
        if b_b<0 or b_b>255: b_b=0

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=get_interplation(),     #dft: cv2.INTER_LINEAR
                            borderMode=borderMode,                  # cv2.BORDER_CONSTANT,  cv2.BORDER_TRANSPARENT
                            borderValue=(b_r,b_g,b_b)               # use with BORDER_CONSTANT
                            )
    return result


#reopen the log to commint it.
def reopen_log():
    global log_file
    log_file.close()
    log_file = open(log_file_name, 'a+')

#take cropped feature and label files and append them verically of horizontally to make one image with two parts
def prepare_append2(file1, file2, the_dir, base_file, counter, disting):
    axis=1       # 0- vertically, 1 - horizontally
    selected = combo_order.get()
    if selected == "Vertically":
        axis = 0  # 0- vertically, 1 - horizontally
    if selected == "Horizontally":
        axis = 1  # 0- vertically, 1 - horizontally

    file_o=os.path.join(the_dir,base_file.replace(".jpg","_"+"{:02d}".format(counter)+disting+save_as,1))  #output file for image
    img1 = cv2.imread(file1)
    img2 = cv2.imread(file2)
    vis = np.concatenate((img1, img2), axis=axis)   # 0- vertically, 1 - horizontally
    cv2.imwrite(file_o, vis)

def run_loading() :
    global results_dir_f, results_dir_l, results_dir_fl,  files, base_dir
    global log_file, log_file_name, result_dirs
    stamp_h = "{:02d}{:02d}".format(datetime.now().hour, datetime.now().minute)
    stamp_d = "{:02d}{:02d}{:02d}_".format(datetime.now().year %100, datetime.now().month, datetime.now().day)+stamp_h
 
    if chk_fixed_folder.get() == True:
        result_dirs="data"
    else:
        result_dirs=stamp_d

    if base_dir == "":
        base_dir = filedialog.askdirectory(title="Parent folder to contain Result Folder")

    if results_dir_f == "":
        results_dir_f=os.path.join(base_dir,result_dirs+"ff")
        if not os.path.exists(results_dir_f):
            os.mkdir(results_dir_f)
        results_dir_log=os.path.join(base_dir,result_dirs+"_log")
        if not os.path.exists(results_dir_log):
            os.mkdir(results_dir_log)
        log_file_name = os.path.join(results_dir_log,  "_log_" + stamp_start + ".log")
        log_file = open(log_file_name, 'wt')
        log_file.write("{} {} of {}\n".format(stamp_start, os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ))
        log_file.write("Log file: {} \n".format(log_file_name))
        print("Log file: ", log_file_name, flush=True)
        total_files_read = sum([len(files) for r, d, files in os.walk(base_dir)])
        text="{} files in {}".format(total_files_read,base_dir)
        label_state.configure(text=text)  # show on the GUI screen
        # r=root, d=directories, f = files
        for r, d, f in os.walk(base_dir):
            for file in f:
                if '.JPG' in file:
                    file1=file.replace(".JPG",".jpg",1)
                    files.append(os.path.join(r, file1))
                if '.jpg' in file:
                    files.append(os.path.join(r, file))
                if '.PNG' in file:
                    file1=file.replace(".PNG",".png",1)
                    files.append(os.path.join(r, file1))
                if '.png' in file:
                    files.append(os.path.join(r, file))
                if '.BMP' in file:
                    file1=file.replace(".BMP",".bmp",1)
                    files.append(os.path.join(r, file1))
                if '.bmp' in file:
                    files.append(os.path.join(r, file))

    if results_dir_l == "":
        results_dir_l=os.path.join(base_dir,result_dirs+"ll")
        if not os.path.exists(results_dir_l):
            os.mkdir(results_dir_l)

    if results_dir_fl == "":
        results_dir_fl=os.path.join(base_dir,result_dirs+"fl")
        if not os.path.exists(results_dir_fl):
            os.mkdir(results_dir_fl)


#=========================================================================================================

def equ_key(key):
    if key=="z" or key=="x" or key=="c" or key=="v" or key=="b":  # like 1,2,3,4,5 in lowest row
        return True
    else:
        return False

def run_rot_f():
    global last_img_f , last_img_v
    run_rot(last_img_f)

def run_rot_v():
    global last_img_f , last_img_v
    run_rot(last_img_v)

def run_rot(last_img):
    angle=int(entry_rot.get())   if entry_rot.get()!='' and entry_rot.get()!=' ' else 0  #
    angle1=int(entry_rot1.get()) if entry_rot1.get()!='' and entry_rot1.get()!=' ' else 0 #
    if angle1!=0 and angle==0:
        angle=-angle1
    if angle!=0:
        img = cv2.imread(last_img)
        img=rotateImage(img, angle)
        cv2.imwrite(last_img ,img)

        cv2.imshow("Rotated", img)
        cv2.waitKey(0)              # wait indefinitely for a key pressed
        cv2.destroyAllWindows()
        print("rot>>>", last_img)
        entry_rot.delete(0, END)
        entry_rot.insert(0, '')
        entry_rot1.delete(0, END)
        entry_rot1.insert(0, '')
    return
#=======================================================================================================

def run_add_f():
    run_add("f")
    global done
    done=done+1
    text = "{}".format(done)
    label_done.configure(text=text)  # show on the GUI screen


def run_add_v():
    run_add("l")

def run_add_full():
    if chk_resize.get() or chk_square.get() or chk_tosize.get() or chk_feature.get() or chk_append2.get():
        text=("Resize, force to square, features and labes order, append 2 result should be unchecked for Add Full.")
        print(text)
        label_state.configure(text=text)  # show on the GUI screen
        return
    print("Add full image:")
    run_add("x")    # force the full image size as the selected size

def run_add(type):
    global inner_counter
    global final_size
    global refPt, cropping, img,  verPt, align, abandon, proceed
    global last_img_f , last_img_v, order
    global title
    global save_as

    title="Select ("+type_name[type.upper()]+") area."

    if chk_feature.get() :
        if (type == 'f' and order%2==1) or  (type != 'f' and order%2==0) :
            print("Button pressed out of order!!!!!!")
            beep()
            return
        order=order+1

    y=int(entry_x.get())  # set for title bar of IrfanView region selection (x, y; w X h)
    x=int(entry_y.get())  #
    h=int(entry_w.get())  #
    w=int(entry_h.get())  #
    angle=int(entry_rot.get())   if entry_rot.get()!='' and entry_rot.get()!=' ' else 0  #
    angle1=int(entry_rot1.get()) if entry_rot1.get()!='' and entry_rot1.get()!=' ' else 0 #
    if angle1!=0 and angle==0:
        angle=-angle1
    proceed=False

    if type == 'f' or type == 'x':
        inner_counter=inner_counter+1

    save_as=entry_save_as.get()

    filename=entry_current.get()  #get input file from gui
    outfile=os.path.basename(filename)

    root, ext = os.path.splitext(outfile)
    root = root.replace('.', '_', 4)  # remove any dot from the middle of the filename
    outfile = root + ext

    print("<<<", filename)
    if filename=='?':
            print("Select file, press Next!!!!!!")
    # crop
    img = cv2.imread(filename)

    if chk_preview.get() == True:    #use internal ROI selection over the image
        #select ROI
        clone = img.copy()
        if chk_fit_big.get():
            cv2.namedWindow(title,cv2.WINDOW_NORMAL) #,cv2.WINDOW_KEEPRATIO) #fit to window size
        else:
            cv2.namedWindow(title)  # show as is, even when big
        cv2.setMouseCallback(title, click_and_crop)
        # keep looping until the 'r' key is pressed
        while True:
            # display the image and wait for a keypress
            cv2.imshow(title, img)
            key = cv2.waitKey(1) & 0xFF     # wait for 1  millisec and exit: key polling
            # print(key)
            # if the 'r' or Esc key is pressed, reset the cropping region
            if key == ord("r") or key == 27 or abandon:
                img = clone.copy()
                refPt = []
                verPt = []
                abandon=False

            # if the 'g' or space key is pressed, break from the loop, accept the action
            elif key == ord("g") or key == ord(" ")  or (key >= ord("1") and key <= ord("9"))or equ_key(key) or proceed:
                proceed = False
                break

        cv2.destroyAllWindows()
        img = clone.copy()  #to remove ROI frame and axis
        if len(refPt) == 2:
            x=refPt[0][1]
            w=refPt[1][1]-x
            y=refPt[0][0]
            h=refPt[1][0]-y
            if w<0:                 # allow rectangle to be started at any angle: from right to left
                x = refPt[1][1]
                w = refPt[0][1] - x
            if h<0:                 # or from down to up
                y = refPt[1][0]
                h = refPt[0][0] - y
            refPt= []   # and forget the region
        else:
            if type == 'x': # force the full image size as the selected size
                x=0
                y=0
                w=img.shape[0]
                h=img.shape[1]
            else:
                print("No ROI was selected, abandon.\n")
                return

        if chk_square.get()==True:  # force cropped image to square form
            if w>h:
                h=w
            elif h>w:
                w=h

        if (chk_resize.get() or chk_square.get()) and chk_tosize.get():
            print("Resize or force to square and set to set cannot be both set.\n")
            chk_tosize.set(False)

        if chk_tosize.get():    # force image to the preset size
            w, h = final_size, final_size
            if x+w>=img.shape[0]:
                x=img.shape[0]-w
            if y+h>=img.shape[1]:
                y=img.shape[1]-h

        entry_x.delete(0, END); entry_x.insert(0, str(y))  # set for title bar of IrfanView region selection (x, y; w X h)
        entry_y.delete(0, END); entry_y.insert(0, str(x))
        entry_w.delete(0, END); entry_w.insert(0, str(h))
        entry_h.delete(0, END); entry_h.insert(0, str(w))
        title="??"
        #end of chk_preview.get() == True  ------------------------------------------

    if len(verPt) == 2: # compute rotation angle using the line drawn by the middle button
        x1v = verPt[0][1]
        x2v = verPt[1][1]
        y1v = verPt[0][0]
        y2v = verPt[1][0]
        dx=x1v-x2v
        dy=y1v-y2v
        angler=math.atan2(dy, dx)  # in radians, between -pi and pi
        angle_d= int(angler * 180.0 / math.pi)  # the angle between x axis and the line, in grades
        angle = -(180+ angle_d)  # make it to be the angle between y axis and the line
        verPt=[]    # and forget the axis

    crop_img = img[ x:x+w, y:y+h] # Crop from {x, y, w, h }
    if angle!=0:
        crop_img=rotateImage(crop_img, angle)

    # resize to the definite size
    if chk_resize.get() ==True:
        final_size=int(entry_resize.get())
        width,height=final_size, final_size
        i256=cv2.resize(crop_img, (width, height), interpolation = get_interplation()) # dft: INTER_LINEAR . INTER_NEAREST  INTER_CUBIC  INTER_LANCZOS4
    else:
        i256=crop_img.copy()


    if type == 'f' or type == 'x':
        the_dir=results_dir_f
    else:
        the_dir=results_dir_l     #select output folder by the image type

    if chk_same_name.get() :
        disting = ""
        ffll = ""
    else:
        disting=type*2 + entry_class.get()     # ll or ff and possibly class type
        ffll="ffll"


    if type == 'x':
        outfile=(outfile.replace(".bmp",".jpg",1)).replace(".png",".jpg",1) # also write output files as jpg
        outfile_f=os.path.join(the_dir,outfile)  #same output file name  for image but as jpg
    else:
        outfile_f=os.path.join(the_dir,outfile.replace(".jpg","_"+"{:02d}".format(inner_counter)+disting+save_as,1))  #output file for image

    cv2.imwrite(outfile_f ,i256)
    print(">>>", outfile_f)

    #keep the names
    if type == 'f' or type == 'x':
        last_img_f=outfile_f
        if chk_feature.get():
            label_last.configure(text="L")  # show next
    elif type == 'l':
        last_img_v=outfile_f
        label_last.configure(text="C")  # show category
        if not chk_fit_big_keep.get():  # if Fit Big Image is not locked then
            chk_fit_big.set(False)  # and remove Fit Big Image setting
    else:
        label_last.configure(text=" ")  # reset last

    if chk_timeout.get():
        timeout = 7000
    else:
        timeout = 0

    cv2.imshow(type.upper(), i256)          # show the cropped image,
    key= cv2.waitKey(timeout) & 0xFF           # wait for any key pressed for 7 seconds and then exit
    cv2.destroyAllWindows()
    log_file.write("\t\t{}\n".format(outfile_f))
    label_state.configure(text="Added: "+outfile_f)  # show on the GUI screen

    if ( not chk_resize.get() and not chk_tosize.get()):
        chk_append2.set(False)

    global file_f
    if chk_append2.get()==True:
        if type == 'f':
            file_f=outfile_f
        else:
            prepare_append2(file_f,outfile_f,results_dir_fl,outfile,inner_counter,ffll)



    entry_rot.delete(0, END)
    entry_rot.insert(0, '')
    entry_rot1.delete(0, END)
    entry_rot1.insert(0, '')

    # shortcut to move to a cathegory folder...
    if type == 'l' and (key == ord("1") or key == ord("z")):
        run_move1()
    if type == 'l' and (key == ord("2") or key == ord("x")):  #
        run_move2()
    if type == 'l' and (key == ord("3") or key == ord("c")):  #
        run_move3()
    if type == 'l' and (key == ord("4") or key == ord("v")):  #
        run_move4()
    if type == 'l' and (key == ord("5") or key == ord("b")):  #
        run_move5()



#======================================================================================

def on_change():
    return

def run_again():
    global inner_counter, order
    global done
    if inner_counter>0:
        inner_counter=inner_counter-1
        order = 0

    done=done-1
    text = "{}".format(done)
    label_done.configure(text=text)  # show on the GUI screen
    print("Counter back to {}\n".format(inner_counter))
    #  run_again

def run_next():
    global current_file_index,current_file, inner_counter
    global last_img_f , last_img_v, order, title
    order=0
    last_img_f=""; last_img_v=""
    label_last_categ.configure(text="-")
    if current_file_index<len(files):
        current_file=files[current_file_index]
        entry_current.delete(0, END)
        entry_current.insert(0, current_file)
        current_file_index=current_file_index+1
        if current_file_index % 5 == 0 :
            reopen_log()
        if current_file_index % 50 == 0:
                beep()
        inner_counter=0
        text = "#{}: {}".format(current_file_index,os.path.basename(current_file))
        label_state.configure(text=text)  # show on the GUI screen
        entry_skip.delete(0, END)
        entry_skip.insert(0, str(current_file_index))
        label_last.configure(text="F")  # show next action

        log_file.write("{}\n".format(text))
        if chk_irfan.get() == True: # use ROI selection in IrfanView
            subprocess.Popen(current_file,  # open the file with default shell command
                             shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        if chk_preview.get() == True:  # p#just preview the image, if required
                if chk_timeout.get():
                    timeout=4000
                else:
                    timeout=0
                img = cv2.imread(current_file)
                entry_x.delete(0, END);   entry_x.insert(0, str(img.shape[1]))  # image size (x, y; w X h)
                entry_y.delete(0, END);   entry_y.insert(0, str(img.shape[0]))
                entry_w.delete(0, END);   entry_w.insert(0, str(0));  entry_h.delete(0, END);  entry_h.insert(0, str(0))  # h, w

                bar_pos=0
                title="The current picture"
                if chk_fit_big.get():
                    cv2.namedWindow(title, cv2.WINDOW_NORMAL)  # ,cv2.WINDOW_KEEPRATIO) #fit to window size
                else:
                    cv2.namedWindow(title)  # show as is, even when big
                cv2.imshow(title, img)              # show the image preview and
                cv2.waitKey(timeout)                   # wait for key to end preview or exit after 4 seconds
                cv2.destroyAllWindows()

    else:
        entry_current.delete(0, END)
        entry_current.insert(0, "")
        label_state.configure(text="No more files.")  # show on the GUI screen

def run_back():
    global current_file_index
    if current_file_index>0:
        current_file_index = current_file_index - 1
        print("Current index back: {}\n".format(current_file_index))
    # run_back

def run_skip():
    global current_file_index
    current_file_index=current_file_index+int(entry_skip.get())  #
    print("Current index skip: {}\n".format(current_file_index))

def run_delete_last():
    global last_img_f , last_img_v
    global done
    if os.path.exists(last_img_f):
        os.remove(last_img_f)
        print("Delete: {}\n".format(last_img_f))
        last_img_f=""
    if os.path.exists(last_img_v):
        os.remove(last_img_v)
        print("Delete: {}\n".format(last_img_v))
        last_img_v=""

    done=done-1
    text = "{}".format(done)
    label_done.configure(text=text)  # show on the GUI screen
    # run delete last

#set folder to move the current image file to (dft C:/Temp) with all its derivatives
def init_move():
    temp_dir = filedialog.askdirectory(title="Parent folder to move to...",initialdir=init_move_to_dir)
    temp_dir=entry_temp.get() 
    entry_temp.delete(0, END)
    entry_temp.insert(0, temp_dir)


# move the current image file to C:/Temp, probably with all its derived images (move all)
def run_move():
    global current_file_index,current_file, inner_counter
    filename=entry_current.get()  #get input file from gui
    temp_dir=entry_temp.get() #"C:/Temp"
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
        print("Created: ", temp_dir)

    selected = combo_move_all.get()
    if selected == "Source" or selected == "All":
        outfile=os.path.join(temp_dir,os.path.basename(filename))
        shutil.move(filename, outfile)  # move file to another folder

        print("Move {} -> {}".format( filename, outfile))
        log_file.write("Move {} -> {}".format( filename, outfile))
        label_state.configure(text="Moved to: "+outfile)  # show on the GUI screen

    if selected == "Sniplets" or selected == "All":
            name_list=os.path.splitext(os.path.basename(filename))
            for suffix in ["ff","fl","ll"]: # for each of tese folders
                a_results_dir_1 = os.path.join(base_dir, result_dirs + suffix)
                a_results_dir_2 = os.path.join(temp_dir, result_dirs + suffix)
                if not os.path.exists(a_results_dir_2):
                    os.mkdir(a_results_dir_2)
                    print("Created: ",a_results_dir_2)
                infile=os.path.join(a_results_dir_1, name_list[0]+'*'+name_list[1])
                for a_file in (glob.glob(infile)):  # find files with the wild-card: all the derived files
                    outfile=os.path.join(a_results_dir_2,os.path.basename(a_file))
                    shutil.move(a_file, outfile)  # move file to another folder
                    print("          {} -> {}".format( infile, outfile))

#############################
#                    move to folders by categories handling
def run_move_i(out_dir_i):
    global current_file_index,current_file,   last_dir
    if (out_dir_i==""):
        return
    last_dir=out_dir_i
    filename=entry_current.get()  #get input file from gui
    label_last.configure(text=" ")  # reset last
    print("==>>> {} -> {}".format( filename, last_dir))
    selected = combo_move_all.get()
    if selected == "Source" or selected == "All":
        outfile=os.path.join(last_dir,os.path.basename(filename))
        shutil.move(filename, outfile)  # move file to another folder

        print("Move {} -> {}".format( filename, outfile))
        log_file.write("Move {} -> {}".format( filename, outfile))
    name_list=os.path.splitext(os.path.basename(filename))
    for suffix in ["ff","fl","ll"]: # for each of tese folders
        a_results_dir_1 = os.path.join(base_dir, result_dirs + suffix)
        a_results_dir_2 = os.path.join(last_dir, result_dirs + suffix)
        if not os.path.exists(a_results_dir_2):
            os.mkdir(a_results_dir_2)
            print("Created: ",a_results_dir_2)
        infile=os.path.join(a_results_dir_1, name_list[0]+'*'+name_list[1])
        for a_file in (glob.glob(infile)):  # find files with the wild-card: all the derived files
            outfile=os.path.join(a_results_dir_2,os.path.basename(a_file))
            if chk_copy.get():
                shutil.move(a_file, outfile)  # move file to another folder
                print("          {} => {}".format( infile, outfile))
            else:
                shutil.copy(a_file, outfile)  # copy file to another folder
                print("          {} -> {}".format( infile, outfile))




def run_move1():
    global current_file_index,current_file,   last_dir, out_dir1
    run_move_i(out_dir1)
    label_last_categ.configure(text="1")
    
def run_to1():                              # create set of folders for a cathegory
    global current_file_index,current_file,  out_dir1
    if config=="":
        out_dir1 = filedialog.askdirectory(title="Parent folder to contain Output Folders /1")
    if out_dir1=="":
        return
    if not os.path.exists(out_dir1):
        os.mkdir(out_dir1)
    button_move_1["text"] = "1->"+os.path.split(out_dir1)[1]
    print("output base/1 ", out_dir1)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir1 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)
                print("Created: ",results_dir_f)


def run_move2():
    global current_file_index,current_file, last_dir, out_dir2
    run_move_i(out_dir2)
    label_last_categ.configure(text="2")

def run_to2():
    global current_file_index,current_file,  out_dir2
    if config=="":
        out_dir2 = filedialog.askdirectory(title="Parent folder to contain Output Folders /2")
    if out_dir2=="":
        return
    if not os.path.exists(out_dir2):
        os.mkdir(out_dir2)
    print("output base/2 ", out_dir2)
    button_move_2["text"] = "2->"+os.path.split(out_dir2)[1]
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir2 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)
                print("Created: ",results_dir_f)


def run_move3():
    global current_file_index,current_file,  last_dir, out_dir3
    run_move_i(out_dir3)
    label_last_categ.configure(text="3")

def run_to3():
    global current_file_index,current_file,  out_dir3
    if config=="":
        out_dir3 = filedialog.askdirectory(title="Parent folder to contain Output Folders /3")
    if out_dir3=="":
        return
    if not os.path.exists(out_dir3):
        os.mkdir(out_dir3)
    button_move_3["text"] = "3->"+os.path.split(out_dir3)[1]
    print("output base/3 ", out_dir3)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir3 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)
                print("Created: ",results_dir_f)


def run_move4():
    global current_file_index,current_file,  last_dir, out_dir4
    run_move_i(out_dir4)
    label_last_categ.configure(text="4")

def run_to4():
    global current_file_index,current_file, out_dir4
    if config=="":
        out_dir4 = filedialog.askdirectory(title="Parent folder to contain Output Folders /4")
    if out_dir4=="":
        return
    if not os.path.exists(out_dir4):
        os.mkdir(out_dir4)
    button_move_4["text"] = "4->"+os.path.split(out_dir4)[1]
    print("output base/4 ", out_dir4)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir4 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)
                print("Created: ",results_dir_f)

def run_move5():
    global current_file_index,current_file,  last_dir, out_dir5
    run_move_i(out_dir5)
    label_last_categ.configure(text="5")

def run_to5():
    global current_file_index,current_file, out_dir5
    if config=="":
        out_dir5 = filedialog.askdirectory(title="Parent folder to contain Output Folders /5")
    if out_dir5=="":
        return
    if not os.path.exists(out_dir5):
        os.mkdir(out_dir5)
    button_move_5["text"] = "5->"+os.path.split(out_dir5)[1]
    print("output base/5 ", out_dir5)
    # r=root, d=directories, f = files
    for r, d, f in os.walk(base_dir):
        for folder in d:
            results_dir_f = os.path.join(out_dir5 , folder)
            if not os.path.exists(results_dir_f):
                os.mkdir(results_dir_f)
                print("Created: ",results_dir_f)


def run_ctrl_z():   # move the files back to the original folders
    global current_file_index,current_file, last_dir
    if last_dir == "":
        print("Cannot undo!!!")
        return
    print("Undo ---------------------------------")
    filename=entry_current.get()  #get input file from gui
    name_list=os.path.splitext(os.path.basename(filename))
    label_last_categ.configure(text="<")
    for suffix in ["ff","fl","ll"]: # for each of tese folders
        a_results_dir_1 = os.path.join(base_dir, result_dirs + suffix)
        a_results_dir_2 = os.path.join(last_dir, result_dirs + suffix)
        infile=os.path.join(a_results_dir_2, name_list[0]+'*'+name_list[1])  # to  get to all _01, _02 etc files
        print("infile: {}".format(infile))
        for a_file in (glob.glob(infile)):  # find files with the wild-card: all the derived files, like _0i 
            orgfile=os.path.join(a_results_dir_1,os.path.basename(a_file))
            undofile=a_file
            print("==orfile: {}".format(orgfile))
            if os.path.exists(undofile):
                shutil.move(undofile, orgfile )  # move file to another folder
                print("*/Undo move:   {} -> {}".format(undofile , orgfile ))
            else:
                print("ERROR: Undo move failed:   {} -> {}".format( undofile, org))



##################

def run_config():
    if config=="":
        print("no config file passed\n");
        return
    run_loading()
    run_to1()
    run_to2()
    run_to3()
    run_to4()
    run_to5()


button_conf = Button(window, text="Config", bg="blue", fg="white", command=run_config)
button_conf.grid(column=0, row=6)   # 6,1

button_init = Button(window, text="Initialize", bg="orange", fg="black", command=run_loading)
button_init.grid(column=0, row=9)   # 6,2

label_1 = Label(window, anchor=E, text="Crop:")
label_1.grid(column=0, row=11)   # widget's location

button_init1 = Button(window, text=" Add F  ", bg="orange", fg="blue", command=run_add_f)
button_init1.grid(column=1, row=12)

button_init1a = Button(window, text=" Rot F  ", bg="orange", fg="blue", command=run_rot_f)
button_init1a.grid(column=3, row=12)

button_init2 = Button(window, text=" Add L  ", bg="orange", fg="green", command=run_add_v)
button_init2.grid(column=1, row=14)

button_init2a = Button(window, text=" Rot L  ", bg="orange", fg="green", command=run_rot_v)
button_init2a.grid(column=3, row=14)

button_again = Button(window, text="Again", bg="orange", fg="red", command=run_again)
button_again.grid(column=4, row=15)

button_init4 = Button(window, text="One Back", bg="orange", fg="blue", command=run_back)
button_init4.grid(column=0, row=16)

button_init3 = Button(window, text="  Next   ", bg="orange", fg="blue", command=run_next)
button_init3.grid(column=1, row=16)

button_full= Button(window, text="Add Full", bg="yellow", fg="green", command=run_add_full)
button_full.grid(column=3, row=16)

button_adel = Button(window, text="Delete\nLast", bg="orange", fg="red", command=run_delete_last)
button_adel.grid(column=4, row=16)

button_init5 = Button(window, text="Skip", bg="orange", fg="blue", command=run_skip)
button_init5.grid(column=0, row=1)

button_init6 = Button(window, text="Move to", bg="orange", fg="blue", command=run_move)
button_init6.grid(column=5, row=6)  # 0,10

button_init7 = Button(window, text="Move to\ninit", bg="orange", fg="blue", command=init_move)
button_init7.grid(column=3, row=6) # 4,10


# buttons to move to categories
label_categ = Label(window, anchor=E, text="Categories:")
label_categ.grid(column=1, row=17)   # widget's location

button_move_1 = Button(window, text="Move 1", bg="orange", fg="green", command=run_move1) # move to its folders
button_move_1.grid(column=1, row=18)
button_init_1 = Button(window, text="Init 1", bg="orange", fg="blue", command=run_to1)  # initialize this output folder
button_init_1.grid(column=2, row=18)

button_move_2 = Button(window, text="Move 2", bg="orange", fg="green", command=run_move2)
button_move_2.grid(column=1, row=19)
button_init_2 = Button(window, text="Init 2", bg="orange", fg="blue", command=run_to2)
button_init_2.grid(column=2, row=19)

button_move_3 = Button(window, text="Move 3", bg="orange", fg="green", command=run_move3)
button_move_3.grid(column=1, row=20)
button_init_3 = Button(window, text="Init 3", bg="orange", fg="blue", command=run_to3)
button_init_3.grid(column=2, row=20)

button_move_4 = Button(window, text="Move 4", bg="orange", fg="green", command=run_move4)
button_move_4.grid(column=1, row=21)
button_init_4 = Button(window, text="Init 4", bg="orange", fg="blue", command=run_to4)
button_init_4.grid(column=2, row=21)

button_move_5 = Button(window, text="Move 5", bg="orange", fg="green", command=run_move5)
button_move_5.grid(column=1, row=22)
button_init_5 = Button(window, text="Init 5", bg="orange", fg="blue", command=run_to5)
button_init_5.grid(column=2, row=22)

button_undo = Button(window, text="UnMove Last", bg="orange", fg="red", command=run_ctrl_z)
button_undo.grid(column=4, row=22)





window.mainloop()   #run the window loop

#termination
stamp=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)
if log_file is not None :
    log_file.write("END: from {} to {} ".format(stamp_start, stamp))
    log_file.close()

print("END: from {} to {}. ".format(stamp_start, stamp), flush=True)
sys.exit(0)
#===============================================================================================================================

