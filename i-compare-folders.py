#compare 2 folder for GAN model data folders to see whether they have fimages with the same names and the same quantity, in any OS.
#Programmed by Michael Sharkansky

import os
import argparse
import subprocess
import time
from datetime import datetime
import numpy as np
import io


#GUI with tkinter, see https://likegeeks.com/python-gui-examples-tkinter-tutorial/
from tkinter.ttk import *
from tkinter import *
from tkinter import filedialog


# init tkinter GUI -----------------------------------------------------------------------------------------
window=Tk() # tkinter start
window.title("Compare folders, V1.2")
window.geometry('980x280')  # window size

label_f1 = Label(window, text="Folder 1")
label_f1.grid(column=0, row=0)

label_f2 = Label(window, text="Folder 2")
label_f2.grid(column=0, row=1)

label_state = Label(window, text="load folders.")
label_state.grid(column=0, row=2)

def run_cmp():
    base_dir1 = filedialog.askdirectory(title="Folder #1")
    base_dir2 = filedialog.askdirectory(title="Folder #2")
    files1 = []
    files2 = []
    len1=0
    len2=0

    if base_dir1 != "":
        print("Folder: ", base_dir1, flush=True)
        label_f1.configure(text="Folder: "+base_dir1)  # show on the GUI screen
        # r=root, d=directories, f = files
        for r, d, f in os.walk(base_dir1):
            for file in f:
                if '.jpg' in file:
                    files1.append(os.path.join(r, file))
                    len1=len1+1

    if base_dir2 != "":
        print("Folder: ", base_dir2, flush=True)
        label_f2.configure(text="Folder: "+base_dir2)  # show on the GUI screen
        # r=root, d=directories, f = files
        for r, d, f in os.walk(base_dir2):
            for file in f:
                if '.jpg' in file:
                    files2.append(os.path.join(r, file))
                    len2=len2+1

    print("folder lengths  {}, {}".format(len1, len2))
    if len1!=len2 :
        print("folder lengths are different: {}, {}".format(len1, len2))

    cnt=0
    for i in range(min(len1,len2)):
        outfile1 = os.path.basename(files1[i])
        outfile2 = os.path.basename(files2[i])
        if outfile1!=outfile2:
            print("different: {}, {}".format(files1[i],files2[i]))
            cnt=cnt+1
        if cnt>3:   # do not scan to the very end, break after coule of lines
            print("and more files down there...\n")
            break
    print("Done.")

button_init = Button(window, text="Go ", bg="orange", fg="black", command=run_cmp)
button_init.grid(column=0, row=4)

window.mainloop()   #run the window loop
