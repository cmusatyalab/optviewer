from cStringIO import StringIO
from zipfile import ZipFile
from flask import Flask, render_template, send_file

# configuration
IMAGE_COLLECTION = '45052.zip'
SCALE_FACTOR = 1.25
SCROLL_SPEED = -10
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
@app.route('/<int:frame>.png')
def tile(frame=None):
    scan = ZipFile(app.config['IMAGE_COLLECTION'])
    frames = sorted(scan.namelist())

    if frame is None:
        nFrames = len(frames)
        keyframes = range(0, nFrames+1, nFrames / 16)
        keyframes[-1] = keyframes[-1]-1
        return render_template('viewer.html',
                               nFrames=nFrames,
                               keyframes=keyframes,
                               SCALE_FACTOR=app.config['SCALE_FACTOR'],
                               SCROLL_SPEED=app.config['SCROLL_SPEED'])

    imgdata = StringIO(scan.read(frames[frame]))
    return send_file(imgdata, mimetype='image/png')

if __name__ == '__main__':
    app.run()

