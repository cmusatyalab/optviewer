from PIL import Image
from cStringIO import StringIO
from zipfile import ZipFile
from flask import Flask, jsonify, render_template, Response, send_file

# configuration
IMAGE_COLLECTION = 'mCF191_%s.zip'
SCALE_FACTOR = 1.25
SCROLL_SPEED = 10
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

PLANES = [ 'Overview', 'Sagittal', 'Coronal', 'Transverse' ]

@app.route('/')
def index():
    scan = ZipFile(app.config['IMAGE_COLLECTION'] % PLANES[1])
    frames = sorted(scan.namelist())

    nFrames = len(frames)
    keyframes = range(0, nFrames+1, nFrames / 16)
    keyframes[-1] = keyframes[-1]-1
    return render_template('viewer.html',
                           nFrames=nFrames,
                           keyframes=keyframes,
                           SCALE_FACTOR=app.config['SCALE_FACTOR'],
                           SCROLL_SPEED=app.config['SCROLL_SPEED'])

@app.route('/<int:plane>/')
def plane(plane):
    scan = ZipFile(app.config['IMAGE_COLLECTION'] % PLANES[plane])
    frames = sorted(scan.namelist())
    return jsonify(plane=plane, name=PLANES[plane], frames=len(frames))

@app.route('/PLANE/FRAME.png')
@app.route('/<int:plane>/<int:frame>.png')
def tile(plane=None, frame=None):
    if plane is None:
        return Response("R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=".decode('base64'),
                        mimetype='image/gif')

    scan = ZipFile(app.config['IMAGE_COLLECTION'] % PLANES[plane])
    frames = sorted(scan.namelist())

    imgdata = StringIO(scan.read(frames[frame]))

    image = Image.open(imgdata)
    if image.format != 'PNG':
        imgdata = StringIO()
        image.save(imgdata, 'PNG')
    imgdata.reset()

    return send_file(imgdata, mimetype='image/png')

if __name__ == '__main__':
    #app.run(host='0.0.0.0')
    app.run()

