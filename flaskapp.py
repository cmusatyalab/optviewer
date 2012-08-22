#
# OPT viewer
#
# Copyright (c) 2012 Carnegie Mellon University
#
# This code is distributed "AS IS" without warranty of any kind under
# the terms of the GNU General Public Licence Version 2, as show in the
# file GPL-LICENSE.txt.
#
from PIL import Image
from cStringIO import StringIO
from zipfile import ZipFile
from flask import Flask, render_template, abort, send_file

# configuration
IMAGE_NAME = 'mCF191'
IMAGE_COLLECTION = '%(name)s_%(plane)s.zip'
DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    scan = ZipFile(app.config['IMAGE_COLLECTION'] % {
        'name': IMAGE_NAME,
        'plane': 'Sagittal',
    })
    frames = sorted(scan.namelist())

    nFrames = len(frames)
    keyframes = range(0, nFrames+1, nFrames / 16)
    keyframes[-1] = keyframes[-1]-1
    return render_template('viewer.html', Name=app.config['IMAGE_NAME'],
                           nFrames=nFrames, keyframes=keyframes)

@app.route('/PLANE/FRAME.png')
@app.route('/<string:plane>/<int:frame>.png')
def image(plane=None, frame=None):
    try:
        plane = plane.lower().capitalize()
        archive = app.config['IMAGE_COLLECTION'] % {
            'name': IMAGE_NAME,
            'plane': plane
        }
        scan = ZipFile(archive)
    except:
        abort(404)

    frames = sorted(scan.namelist())
    imgdata = StringIO(scan.read(frames[frame]))

    image = Image.open(imgdata)
    if image.format != 'PNG':
        imgdata = StringIO()
        image.save(imgdata, 'PNG')
    imgdata.reset()

    return send_file(imgdata, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

