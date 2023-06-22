#batch run resize/rescale sequence of images into another size and make them all png (default). The current version, any OS.
#Programmed by Michael Sharkansky

import os
import argparse
import subprocess
import time
from datetime import datetime
import numpy as np
import io
import cv2  # use: pip install opencv-contrib-python
#import winsound

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

final_size=256          #final size of cropped and resized to square image
save_as = ".png"        #to save as jpg (or png or bmp)

print(os.getcwd(), flush=True)  # print working dir (import os)
print("Running {}, {}.".format(os.path.realpath(__file__), time.ctime(os.path.getmtime(__file__)) ) , flush=True)
stamp_start=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)

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
file_f=""
suffix=""
resize_string="Resize to size of"
scale_string ="Scale to pcnt of"
none_string  ="None"

# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Batch resize / rescale")
window.geometry('950x300')  # window size

label_s = Label(window, anchor=E, text="Class suffix:")
label_s.grid(column=1, row=0)   # widget's location

entry_suf = Entry(window, width=5)  # suffix for filename (like _s)
entry_suf.grid(column=2, row=0)
entry_suf.insert(0, '') #put text into the entry widget

label_ifile = Label(window, anchor=E, text="Current file:")
label_ifile.grid(column=4, row=0)   # widget's location

entry_current = Entry(window, width=90)  # THE FILE NAME INPUT widget
entry_current.grid(column=6, row=0)  # location within the window
entry_current.insert(0, "?")

entry_skip = Entry(window, width=8)  # skip files  widget
entry_skip.grid(column=2, row=1)  # location within the window
entry_skip.insert(0, "0")

# chk_resize=BooleanVar()     # resize/scale the cropped image to the preset size (not togeher with tosize)
# chk_resize.set(True)
# chk_box_resize = Checkbutton(window, text="Resize", var=chk_resize)
# chk_box_resize.grid(column=6, row=9)

entry_resize = Entry(window, width=8)  # side size for resize
entry_resize.grid(column=6, row=10)  # location within the window
entry_resize.insert(0, str(final_size))

combo_act = Combobox(window)
combo_act['values'] = (resize_string,  scale_string, none_string)      # resize/scale/rotate interpolation
combo_act.current(0)  # set the selected item
combo_act.grid(column=6, row=9)

combo_inter = Combobox(window)
combo_inter['values'] = ("INTER_LINEAR",  "INTER_AREA",  "INTER_NEAREST", "INTER_CUBIC", "INTER_LANCZOS4", "DEFAULT" )      # resize interpolation
combo_inter.current(0)  # set the selected item
combo_inter.grid(column=6, row=12)


chk_same_name=BooleanVar()    # keep same name of output images
chk_same_name.set(True)
chk_box_same_name = Checkbutton(window, text="Output to the same name", var=chk_same_name)
chk_box_same_name.grid(column=6, row=13)


chk_fit_big=BooleanVar()     # fit big image to window, good when selectinf feature/label, can changed at any time
chk_fit_big.set(False)
chk_box_fit_big = Checkbutton(window, text="Fit big\nimage", var=chk_fit_big)
chk_box_fit_big.grid(column=3, row=15)

label_bl1 = Label(window, anchor=E, text="-")
label_bl1.grid(column=0, row=2)   # widget's location

# set for the title bar of IrfanView region selection (x, y; w X h)
label_xy = Label(window, anchor=E, text="X,Y,W,H")
label_xy.grid(column=0, row=3)   # widget's location

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


label_rot = Label(window, anchor=E, text="Rotate CCW\n+ <= -")
label_rot.grid(column=3, row=12)   # widget's location

entry_rot = Entry(window, width=5)  # counter-clockwise rotation angle
entry_rot.grid(column=3, row=13)
entry_rot.insert(0, '') #put text into the entry widget

label_rot1 = Label(window, anchor=E, text="Rotate CW\n =>")
label_rot1.grid(column=1, row=12)   # widget's location

entry_rot1 = Entry(window, width=5)  # clockwise rotation angle
entry_rot1.grid(column=1, row=13)
entry_rot1.insert(0, '') #put text into the entry widget

label_last = Label(window, text="*")
label_last.grid(column=2, row=13)

label_state = Label(window, text="Waiting for init.")
label_state.grid(column=6, row=16)

#--------------------------------------------------------------------------------------------
def beep():
    frequency = 80  # Set Frequency To 800 Hertz
    duration = 500  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)


# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False
close_window=False


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

def get_interplation():
    #"INTER_LINEAR", "INTER_NEAREST", "INTER_AREA", "INTER_CUBIC", "INTER_LANCZOS4"
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
#=====================================================================================

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
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=get_interplation())
    return result


#reopen the log to commint it.
def reopen_log():
    global log_file
    log_file.close()
    log_file = open(log_file_name, 'a+')

#take cropped feature and label files and append them verically of horizontally to make one image with two parts
def prepare_append2(file1, file2, the_dir, base_file, counter, disting):
    axis=1       # 0- vertically, 1 - horizontally
    file_o=os.path.join(the_dir,base_file.replace(".jpg","_"+"{:02d}".format(counter)+disting+save_as,1))  #output file for image
    img1 = cv2.imread(file1)
    img2 = cv2.imread(file2)
    vis = np.concatenate((img1, img2), axis=axis)   # 0- vertically, 1 - horizontally
    cv2.imwrite(file_o, vis)

def run_loading() :
    global results_dir_f, results_dir_l, results_dir_fl,  files, base_dir
    global log_file, log_file_name
    stamp_h = "{:02d}{:02d}".format(datetime.now().hour, datetime.now().minute)
    stamp_d = "{:02d}{:02d}{:02d}_".format(datetime.now().year %100, datetime.now().month, datetime.now().day)+stamp_h

    if base_dir == "":
        base_dir = filedialog.askdirectory(title="Parent folder to contain Result Folder")

    if results_dir_f == "":
        results_dir_f=os.path.join(base_dir,stamp_d+"ff")
        os.mkdir(results_dir_f)
        log_file_name = os.path.join(results_dir_f,  "_log_" + stamp_start + ".log")
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


#=========================================================================================================

def run_rot_f():
    global last_img_f , last_img_v
    run_rot(last_img_f)

def run_rot_v():
    global last_img_f , last_img_v
    run_rot(last_img_v)

def run_rot(last_img):
    angle=int(entry_rot.get())   if entry_rot.get()!='' else 0  #
    angle1=int(entry_rot1.get()) if entry_rot1.get()!='' else 0 #
    if angle1!=0 and angle==0:
        angle=-angle1
    if angle!=0:
        img = cv2.imread(last_img)
        img=rotateImage(img, angle)
        cv2.imwrite(last_img ,img)

        cv2.imshow("Rotated", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        print("rot>>>", last_img)
        entry_rot.delete(0, END)
        entry_rot.insert(0, '')
        entry_rot1.delete(0, END)
        entry_rot1.insert(0, '')
    return
#=======================================================================================================


def run_add(type):
    global inner_counter
    global final_size
    global refPt, cropping, img, close_window
    global last_img_f , last_img_v
    global title
    global suffix

    title="The image ("+type.upper()+")"


    y=int(entry_x.get())  # set for title bar of IrfanView region selection (x, y; w X h)
    x=int(entry_y.get())  #
    h=int(entry_w.get())  #
    w=int(entry_h.get())  #
    angle=int(entry_rot.get())   if entry_rot.get()!='' else 0  #
    angle1=int(entry_rot1.get()) if entry_rot1.get()!='' else 0 #
    if angle1!=0 and angle==0:
        angle=-angle1

    filename=entry_current.get()  #get input file from gui
    outfile=os.path.basename(filename)
    print("<<<", filename)
    if filename=='?':
            print("Select file, press Next!!!!!!")
    # crop
    img = cv2.imread(filename)

    x = 0
    y = 0
    w = img.shape[0]
    h = img.shape[1]

    crop_img = img[ x:x+w, y:y+h] # Crop from {x, y, w, h }

    # resize to the definite size
    selected = combo_act.get()
    if selected == resize_string:
        final_size=int(entry_resize.get())
        width,height=final_size, final_size
        i256=cv2.resize(crop_img, (width, height), interpolation = get_interplation()) # dft: INTER_LINEAR . INTER_NEAREST  INTER_CUBIC  INTER_LANCZOS4
    elif selected == scale_string:
        percent=float(entry_resize.get())/100.0
        width=int(crop_img.shape[1] * percent)
        height=int(crop_img.shape[0] * percent)
        i256=cv2.resize(crop_img, (width, height), interpolation = get_interplation()) # dft: INTER_LINEAR . INTER_NEAREST  INTER_CUBIC  INTER_LANCZOS4
    else:
        i256=crop_img.copy()

    if angle!=0:
        i256=rotateImage(i256, angle)

    if type == 'f' or type == 'x':
        the_dir=results_dir_f
    else:
        the_dir=results_dir_l     #select output folder by the image type

    if chk_same_name.get() :
        disting = ""
        ffll = ""
    else:
        disting=type*2      # ll or ff
        ffll="ffll"

    if type == 'x':
        outfile=((outfile.replace(".bmp",save_as,1)).replace(".jpg",save_as,1)).replace(".png",save_as,1) # also write output files as png
        outfile=outfile.replace(save_as, suffix+save_as, 1)
        outfile_f=os.path.join(the_dir,outfile)  #same output file name  for image but as jpg
    else:
        outfile_f=os.path.join(the_dir,outfile.replace(".jpg","_"+"{:02d}".format(inner_counter)+disting+save_as,1))  #output file for image

    cv2.imwrite(outfile_f ,i256)
    print(">>>", outfile_f)

    #keep the names
    last_img_f = outfile_f
    last_img_v = outfile_f

    log_file.write("\t\t{}\n".format(outfile_f))
    label_state.configure(text="Added: "+outfile_f)  # show on the GUI screen

    global file_f
    # if chk_append2.get()==True:
    #     if type == 'f':
    #         file_f=outfile_f
    #     else:
    #         prepare_append2(file_f,outfile_f,results_dir_fl,outfile,inner_counter,ffll)

    entry_rot.delete(0, END)
    entry_rot.insert(0, '')
    entry_rot1.delete(0, END)
    entry_rot1.insert(0, '')


#======================================================================================

def on_change():
    return

def run_next():
    global current_file_index,current_file, inner_counter
    global last_img_f , last_img_v, suffix, log_file
    last_img_f=""; last_img_v=""
    suffix=entry_suf.get() # add suffix

    for current_file_index in range(len(files)):
        current_file=files[current_file_index]
        entry_current.delete(0, END)
        entry_current.insert(0, current_file)
        current_file_index=current_file_index+1
        if current_file_index % 100 == 0:
            reopen_log()
            beep()
        inner_counter=0
        text = "#{}: {}".format(current_file_index,current_file)
        label_state.configure(text=text)  # show on the GUI screen
        entry_skip.delete(0, END)
        entry_skip.insert(0, str(current_file_index))
        run_add("x")

        log_file.write("{}\n".format(text))

    selected = combo_act.get()
    if selected == resize_string:
        final_size=int(entry_resize.get())
        print("action done: resize to {} pixels.".format(final_size))
    elif selected == scale_string:
        percent=float(entry_resize.get())/100.0
        print("action done: rescale to {} ratio.".format(percent))
    else:
        print("action done: just copy images in {} format.".format(save_as))

    entry_current.delete(0, END)
    entry_current.insert(0, "")
    label_state.configure(text="No more files.")  # show on the GUI screen
    stamp=(((str(datetime.now())).replace('.','-',4)).replace(':','-',4)).replace(' ','_',4)
    if log_file is not None :
        log_file.write("END: from {} to {} ".format(stamp_start, stamp))
        log_file.close()
        log_file=None



def run_skip():
    global current_file_index
    current_file_index=current_file_index+int(entry_skip.get())  #
    print("Current index: {}\n".format(current_file_index))

def run_reset():
    global base_dir,  files, current_file_index, results_dir_f, results_dir_l, results_dir_fl
    base_dir = ""
    results_dir_f = ""  # feature folder
    results_dir_l = ""  # label folder
    results_dir_fl = ""  # feature+label folder
    files = []
    current_file_index = 0
    print("Reset.")

button_init = Button(window, text="Init ", bg="orange", fg="black", command=run_loading)
button_init.grid(column=6, row=2)

label_2 = Label(window, anchor=E, text="-")
label_2.grid(column=0, row=13)   # widget's location

label_3 = Label(window, anchor=E, text="-")
label_3.grid(column=0, row=15)   # widget's location

button_init3 = Button(window, text="Go", bg="orange", fg="blue", command=run_next)
button_init3.grid(column=2, row=16)

button_init5 = Button(window, text="Skip", bg="orange", fg="blue", command=run_skip)
button_init5.grid(column=0, row=1)

button_reset = Button(window, text="Reset ", bg="orange", fg="black", command=run_reset)
button_reset.grid(column=6, row=15)

window.mainloop()   #run the window loop

#termination
stamp = (((str(datetime.now())).replace('.', '-', 4)).replace(':', '-', 4)).replace(' ', '_', 4)
print("END: from {} to {}. ".format(stamp_start, stamp), flush=True)
sys.exit(0)
#===============================================================================================================================

