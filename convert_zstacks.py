import numpy as np
from PIL import Image
import argparse
import os

try:
  from progressbar import ProgressBar
except ImportError:
  def ProgressBar():
    return lambda x: x

parser = argparse.ArgumentParser()
parser.add_argument('--edgelength', type=int, default=512)
parser.add_argument('assay')
args = parser.parse_args()

assay = os.path.basename(args.assay)
path = os.path.join("%(path)s_%%s" % args.assay,
                    "%(assay)s_rec%%04d.bmp" % assay)

ZSTACKS = 1024

print "Checking if all images are available"
progress = ProgressBar()
for i in progress(range(ZSTACKS)):
    for section in ['VIS', 'GFP1']:
        q = path % (section, i)
        if not os.path.exists(q):
            print "\nMissing", q

volume_shape = (args.edgelength,)*3 + (3,)
volume = np.zeros(volume_shape, dtype=np.uint8)

print "Loading image data"
progress = ProgressBar()
for i in progress(range(volume.shape[2])):
    index = int(i * ZSTACKS / args.edgelength)
    img = Image.open(path % ('VIS', index))
    img = img.resize(volume.shape[:2], Image.NEAREST)
    volume[:,:,i,0] = np.asarray(img)

    img = Image.open(path % ('GFP1', index))
    img = img.resize(volume.shape[:2], Image.NEAREST)
    volume[:,:,i,1] = np.asarray(img)


print "Saving transverse slices"
path = os.path.join(args.assay, 'transverse')
os.makedirs(path)
progress = ProgressBar()
for i in progress(range(volume.shape[0])):
    img = Image.fromarray(np.rot90(volume[i,:,:]))
    img.save(os.path.join(path, '%04d.png' % i))

print "Saving sagittal slices"
path = os.path.join(args.assay, 'sagittal')
os.makedirs(path)
progress = ProgressBar()
for i in progress(range(volume.shape[1])):
    img = Image.fromarray(np.rot90(volume[:,i,:]))
    img.save(os.path.join(path, '%04d.png' % i))

print "Saving coronal slices"
path = os.path.join(args.assay, 'coronal')
os.makedirs(path)
progress = ProgressBar()
N = volume.shape[2] - 1
for i in progress(range(volume.shape[2])):
    img = Image.fromarray(volume[:,:,i])
    img.save(os.path.join(path, '%04d.png' % N-i))

