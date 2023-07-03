# Python-image-preprocessing-for-GAN

			Pre-editing Python programs
			Programmed by Michael Sharkansky

			Overview
			
i-crop-batch – run in a batch mode over a folder with images  and create images resized to a definite 
side size or images re-scaled to percents of the original images. Place the resulting images into another 
folder.
i-crop-list-roi  – process sequence of images in a folder and create one or two sets of images cut from 
each original image. It can be used to cut features form images or to cut couples of features and labels 
from images.  Command line:   -c  <config_file>
i-select  -  for GAN model data: run in a main folder and leave or move files to another folders, I.e. 
take a file and possibly move all the files with this name from parallel folders to parallel folders in 
another directory: 
  a/f/pic1.jpg -> b/f/pic1.jpg 
  a/l/pic1.jpg -> b/l/pic1.jpg 
  a/fl/pic1.jpg -> b/fl/pic1.jpg 
and so on for each selected file. 
The purpose is to clean image set of low quality images. The best way is to run on the folder with 
appended feature/label images, which is set as a leading sub-folder. 
This sub-folder of the appended images can be created by running i-list-append2.py over feature 
folder and label folder.

i-select-cat  -  to split image set into categories data sets: run in a main folder and leave or move files 
to a group of another folders take a file and possibly move all the files with this name from parallel 
folders to parallel folders in another directory: 
 a/f/pic1.jpg -> b/f/pic1.jpg 
 a/l/pic1.jpg -> b/l/pic1.jpg 
 a/fl/pic1.jpg -> b/fl/pic1.jpg 
 and so on for each selected file. 
The purpose is to divide image set into several categories of images. The best way is to run on the 
folder with appended feature/label images, which is set as a leading sub-folder. 
This folder of appended images can be created by running i-list-append2.py over feature folder and 
label folder.
Command line:   -c  <config_file> 

i-list-append2  –  take images with the same name from 2 folders and append them into one image, 
horizontally or vertically. Take an image and split it into two halves, horizontally or vertically.

i-list-appendN  –  take images with the same name from N folders listed in the configuration file 
(default configuration file is: conf_append_n.txt) and append them into one image, horizontally or 
vertically. 

i-list-append_next - append pairs of consecutive images in a folder into a larger image and place the 
resulting images into another folder. It is useful when feature is on one image and the label is on the 
next one (or vice versa).  A program named “counters.exe” copies a pair of images with appending a 
running number to them so that they remain consecutive in the folder.

i-compare-folders – compare two folder to verify that they contain the same file names for all the files 
in both folders, feature and label. It is for the GAN models.

i-folder-files – remove a number of files from all the subfolders or copy or move a number of files into 
the corresponding subfolder in another folder. It is for the GAN models to help to maintain files in 
folders with feature and label subfolders. Command line:   -c  <config_file> 
The selections of from line “I” to line “j” will process the I-th line, the j-th line and all the lines between 
them: it processes j-i+1 images.

Taftaf-class-u – run classification deep learning models.

i-find-image – find image with same name in another folder and show it. Good for feature/label sets 
of folders.

i-make-list  - append a sequence of images into one file.

i-make-rename  - remove ‘ll’ or ‘ff’ from the file names.


 
				Detailed description

i-crop-list-roi

Command line:   -c  <config_file> 

Initialize – the 1st button: select folder with images and create subfolders for results.
Skip – skip q-ty of images in the following edit control
INTR_LINEAR combo – select algorithm for image resizing
Resize checkbox – resize result images to the size below
256 edit - size of result images

Force to square form checkbox – force cropped picture to be square of any size, unscaled (not to be 
checked together with ‘Force to this size’)

Force to this size checkbox - force cropped picture to be square of preset size, when an unscaled 
square of the given size must be cropped from the image

Output to the same name checkbox – give the same file name to result images
Feature and Label order checkbox – ensure that Add F and Add L buttons are called in the correct 
order: Add F is the 1st.  It should be unchecked if no Label images are needed.
Append 2 results checkbox – create a subfolder to store appended resulting feature and labels
Horizontally combo – append either horizontally or vertically
IrfanView checkbox – preview with IrfanView
Preview check box – preview with the internal viewer. The previewed image is closed by space tab. 
The mouse can select a region over the image by clicking the left mouse button and dragging the 
mouse until the button release. Any rectangle corner may be started at. It is marked by a small red 
cross. The assumed vertical axis of the image is selected by clicking the middle mouse button and 
dragging it until the button release. The drawn assumed axis will cause the image of the selected 
region to be rotated with the angle between the assumed vertical axis and the real vertical axis of the 
screen. The region and the axis are discarded by Esc. The confirmation of selection is done by ‘space’ 
key.
The preview image is confirmed by ‘space’ key and stays in the results folder. A 1 to 5 key for the label 
result move it and its feature image to the 1st to 5th category appropriate folders.
X, Y, W, H – enter the ROI selected in the IrfanView
Next – go to the next image
One Back – return one image back (also many times)
Add Full – take the entire image as result. If this button is used, “Resize”, “Force to Square form”, 
“Features and Labels Order”, “Append 2 results” should be unchecked. The image may be rotated 
using rotate buttons or the assumed vertical axis line created with the middle mouse button.
Rotate CW edit – angle to which the image is rotated clockwise
Rotate CCW edit  -angle to which image is rotated counterclockwise
Add F – show image to select the feature and rotate it by the angle in Rotate edit control
Add L – show image to select the label and rotate it by the angle in Rotate edit control
Rotate F - rotate the feature image by the angle in Rotate edit controls and display the result
Rotate L - rotate the label image by the angle in Rotate edit controls and display the result
Again – discard already selected result images and allow to use Add F and Add L again
Fit Big Image checkbox – fit big image view into the screen size (view is distorted).  The Checkbox is 
reset when the image is fully processed, unless always checkbox is set.
Always checkbox -  do not reset the Fit Big Image checkbox on image processing completion.usefull 
whe most f the images in the set are vary large.
RButton combo-box – “Commit/up” causes right button up to serve as “space” key to proceed with 
the image, “Re-center/dbl” causes the place of right button double click to become the center of the 
selected image region.
Move to – move the result files to the subfolder in the folder in the edict control at the right as Source 
(source file), Sniplets (result files), All (both of them)
Delete last – delete the last set of results.
Save as -  save as .jpg or .png
Class – append this string to the filenames. Good to separate the files into groups later.
Category selection – move the derived images into a category folder
Move checkbox – move to category folder if checked, otherwise – copy.
Undo Last  - return the last set of images from a category folder to the results folder.
Close on timeout – causes the preview and approval widows to be closed after several seconds.


i-crop-batch – run in a batch mode over a folder with images  and create images resized to a definite 
side size or images rescaled to percents of the original images in another folder.
Initialize – the 1st button: select folder with images and create subfolders with results in it.
INTR_LINEAR combo – select algorithm for image resizing
Resize checkbox – resize result images to the size below or to percentage below
256 edit - size of result images or percentage of original image
Output to the same name checkbox – give the same file name to result images
Reset – clear all previous settings. Good before another batch.
Skip – skip q-ty of images in the following edit control
Class – append this string to the filenames. Good to separate the files into groups later.
Go  - start the batch processing.
X, Y, W, H – show size of the current image
Rotate CW edit – angle to which the image is rotated clockwise
Rotate CCW edit  - angle to which the  image is rotated counterclockwise


i-list-append2  
takes the images with the same name from 2 folders and append them into one image, horizontally or 
vertically. Take an image and split it into two halves, horizontally or vertically. 

Orientation – append images horizontally or vertically
Initialize for Append – set folders of files to be appended and result files folder. The 1st image is called 
feature, the 2nd is called label.
Init for next Append – takes the output folder and allows to append to it from another folder.
Append – start batch run.

Automatic orientation check-box – determine automatically how the files should be splitter: vertically 
or horizontally. If not check, Orientation combo defines the split line.

For the 1st part combo and edit – the first image in 1/n part of the entire image, or the first pat has p 
pixels.
Split – set folders and run split batch.

i-list-append_next
Takes the 2 consecutive images  from a folder and append them into one image, horizontally or 
vertically, naming it after the 1st image, adding a suffix to the output file names, default is “_d”.
Each pair of images must have at least one of their dimensions to be the same and in accordance with 
the “orientation” selection.
Orientation – append images horizontally or vertically. “Long” causes  images to be appended along 
their  longest dimension.
Initialize for Append – set folder to hold the results and the folder from which to append couples of 
consecutive images. 
Auto Resize – if checked, the application corrects the cases when there is a different size along the 
appending axis dimension. 
Append – start batch run.

i-select  
For GAN model data: run in a main folder and leave or move files to another folders take a file and 
possibly move all the files with this name from parallel folders to parallel folders in another directory: 
 a/f/pic1.jpg -> b/f/pic1.jpg 
 a/l/pic1.jpg -> b/l/pic1.jpg 
 a/fl/pic1.jpg -> b/fl/pic1.jpg 
 and so on for each selected file. 
The purpose is to clean image set of low quality images. The best way is to run on the folder with 
appended feature/label images. 
This folder of appended images can be created by running i-append.py over feature folder and label 
folder.
Init - set folders.
Skip – skip q-ty of images in the following edit control.
Next  - Select next image and show it. Space bar closes the image view.
Move – move this image to the other folder.
One back – return back to the previous image.
Fit big image checkbox – resize big image display to fit he screen.
i-compare-folders 
compares two folder to verify that they contain the same file names for all the files in both folders. It is 
for the GAN models.
Go –select the two folders to compare and run the comparison. The result is displayed on console 
window or the output window.

--- *** ---
