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

# http://flask.pocoo.org/snippets/35/
class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app = Flask(__name__)
app.config.from_object(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

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

