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
path = "%(path)s_%%s/%(assay)s_rec%%04d.bmp" % {
    'path': args.assay,
    'assay': assay,
}

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
os.makedirs('%s/transverse' % args.assay)
progress = ProgressBar()
for i in progress(range(volume.shape[0])):
    img = Image.fromarray(np.rot90(volume[i,:,:]))
    img.save('%s/transverse/%04d.png' % (args.assay, i))

print "Saving sagittal slices"
os.makedirs('%s/sagittal' % args.assay)
progress = ProgressBar()
for i in progress(range(volume.shape[1])):
    img = Image.fromarray(np.rot90(volume[:,i,:]))
    img.save('%s/sagittal/%04d.png' % (args.assay, i))

print "Saving coronal slices"
os.makedirs('%s/coronal' % args.assay)
progress = ProgressBar()
N = volume.shape[2] - 1
for i in progress(range(volume.shape[2])):
    img = Image.fromarray(volume[:,:,i])
    img.save('%s/coronal/%04d.png' % (args.assay, N-i))

