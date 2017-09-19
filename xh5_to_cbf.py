"""
author:
Tobiasz Jarosiewicz

Read a XFEL h5 file, retrieve images, write them to cbf format.
Option -D to display the image on screen.
"""

import h5py
import fabio
import numpy as np
import sys
try:
    import cPickle as pickle
except ImportError:
    import pickle
from pprint import pprint
from PIL import Image
from optparse import OptionParser
import collections

port = None
port = None
topic = None

# Option parsing:
usage = "Usage: {} [options] <file name> ".format(sys.argv[0]) 
parser = OptionParser(usage=usage)
parser.add_option("-n", "--number_of_images", dest="numrange",
                  help="Specify how many images to process \
                  for the range from 0 to <n>", default=1)
parser.add_option("-D", "--display", action="store_true", dest='display', 
                  help="Use this option to display the images on screen.", 
                  default = 0)
parser.add_option("-S", "--save_image_NOT", action="store_false", dest='saveimage', 
                  help="Don't save the cbf file. ", 
                  default = 1)
parser.add_option("-P", "--png_file", action="store_true", dest='pngsave', 
                  help="Use this option to save the image to a png file.", 
                  default = 0)
(options, args) = parser.parse_args()

nrange = int(options.numrange)
disp_flag = options.display
save_flag = options.saveimage
png_flag = options.pngsave

# Image dimmensions are specified here. 
w, h = 256, 256

# Selecting values only from a given key (as a parameter).
def filter_dict_by_key(dictInput, kname):
    if kname in dictInput.keys():
        return dictInput[kname]

# Needed for visit() to work.
def printname(name):
    print(name)

try:
    h5name = sys.argv[1]
    print("Loading file: {}".format(h5name))
except IndexError:
    print(usage)
    exit(1)

# Loading the hdf file
try:
    tmpf = h5py.File(h5name, 'r')
except IOError:
    print("Check input file.")
    exit(1)

# To see the structure of the loaded file:
#tmpf.visit(printname)

# Step by step descending into h5 file tree structure:
data_instr = filter_dict_by_key(tmpf, 'INSTRUMENT')
data_detct = filter_dict_by_key(data_instr, 'DETLAB_LAB_DAQ-0')
data_detct2 = filter_dict_by_key(data_detct, 'DET')
data_xtdf = filter_dict_by_key(data_detct2, '0:xtdf')
data_images = filter_dict_by_key(data_xtdf, 'image')
data_img_asd = filter_dict_by_key(data_images, 'data')

# This part is not really needed, it is possible to access the data 
# with specifying path to images like:
data_img_data = tmpf["INSTRUMENT/DETLAB_LAB_DAQ-0/DET/0:xtdf/image/data"]
# This is the point when the dataset with images is reached.

# Create empty array for image:
img_to_show = np.zeros((h, w), dtype=np.uint8)

i = 0
# Loop for iterating through each image [pulse?] - sample data (0:5039)
for im_dset in data_img_data:
    # Prefix for file name:
    img_filename = ''
    # Copying the array while reducing 1 dimmension:
    img_reduced = im_dset[0, ...]
    header = {}
    cbf_out = fabio.cbfimage.cbfimage(header=header,data=img_reduced)
    img_to_show = img_reduced
    img = Image.fromarray(img_to_show, 'L')
    # Preparing file names:
    for key_a in data_detct2.keys():
        img_prefix = str(key_a)
        img_filename = ''.join(filter(str.isalpha, img_prefix))
        cbf_filename = img_filename + '_img{}.cbf'.format(i)
        png_filename = img_filename + '_img{}.png'.format(i)
    if save_flag == 1:
        print('saving image to: {}'.format(cbf_filename))
        cbf_out.write(cbf_filename)
    if png_flag == 1:
        print('saving image to: {}'.format(png_filename))
        img.save(png_filename)
    if disp_flag == 1:
        img.show()
    i += 1
    if i >= nrange:
        exit(1)
