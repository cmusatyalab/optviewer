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
from flaskext.script import Manager
from flask_snippets import ReverseProxied

# configuration
IMAGE_NAME = 'mCF191'
IMAGE_COLLECTION = '%(name)s_%(plane)s.zip'
DEBUG = False

app = Flask(__name__)
app.config.from_object(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

@app.route('/')
def index():
    scan = ZipFile(app.config['IMAGE_COLLECTION'] % {
        'name': app.config['IMAGE_NAME'],
        'plane': 'Sagittal',
    })
    nFrames = len(scan.namelist())
    scan.close()
    return render_template('viewer.html', Name=app.config['IMAGE_NAME'],
                           nFrames=nFrames)

@app.route('/NAME/PLANE/FRAME1.png')
@app.route('/<string:name>/<string:plane>/<int:frame>.png')
def image(name=None,plane=None, frame=None):
    try:
        plane = plane.lower().capitalize()
        archive = app.config['IMAGE_COLLECTION'] % { 'name': name, 'plane': plane }
        scan = ZipFile(archive)
    except:
        abort(404)

    frames = sorted(scan.namelist())
    imgdata = StringIO(scan.read(frames[frame]))
    scan.close()

    image = Image.open(imgdata)
    if image.format != 'PNG':
        imgdata = StringIO()
        image.save(imgdata, 'PNG')
    imgdata.reset()

    return send_file(imgdata, mimetype='image/png')


manager = Manager(app)

@manager.command
def make_static_site(path):
    """Create a static site under <path>"""
    import os, shutil, sys

    if os.path.exists(path):
        print path, "already exists, exiting"
        sys.exit(1)

    IMAGE_NAME = app.config['IMAGE_NAME']

    for plane in ['sagittal', 'coronal', 'transverse']:
        z = ZipFile(app.config['IMAGE_COLLECTION'] % {
            'name': IMAGE_NAME, 'plane': plane.capitalize(),
        })
        z.extractall(path=os.path.join(path, IMAGE_NAME, plane))
        nFrames = len(z.namelist())
        z.close()

    with open(os.path.join(path, 'index.html'), 'w') as f:
        html = render_template('viewer.html', Name=IMAGE_NAME, nFrames=nFrames)
        # convert to relative URLs
        html = html.replace('/static/', 'static/')
        html = html.replace('/NAME/', 'NAME/')
        f.write(html)

    shutil.copytree('static', os.path.join(path, 'static'))

if __name__ == '__main__':
    manager.run()

