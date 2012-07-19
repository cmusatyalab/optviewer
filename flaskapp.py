from PIL import Image
from cStringIO import StringIO
from zipfile import ZipFile
from openslide import ImageSlide
from openslide.deepzoom import DeepZoomGenerator

from flask import Flask, render_template, abort
app = Flask(__name__)

class ImageZoom(ImageSlide):
    def __init__(self, *args, **kwargs):
        super(ImageZoom, self).__init__(*args, **kwargs)
        self._zoomlevels = kwargs.get('maxzoom', 3)

    @property
    def level_count(self):
        return self._zoomlevels+1

    @property
    def level_dimensions(self):
        return [ tuple(s << level for s in self._image.size)
                 for level in xrange(self._zoomlevels, -1, -1) ]

    @property
    def level_downsamples(self):
        return [ float(1 << l) for l in xrange(self._zoomlevels+1) ]

    def get_best_level_for_downsample(self, downsample):
        downsamples = self.level_downsamples
        for i, sample in enumerate(downsamples):
            if downsample < sample:
                return i - 1
        return self._zoomlevels
        
    def read_region(self, location, level, size):
        location = [ l >> self._zoomlevels for l in location ]
        region_size = [ s >> (self._zoomlevels - level) for s in size ]
        region = super(ImageZoom, self).read_region(location, 0, region_size)
        return region.resize(size, Image.NEAREST)

@app.route('/')
@app.route('/<int:layer>/<int:z>/<int:x>/<int:y>.png')
def tile(layer=0, z=None, x=None, y=None):
    scan = ZipFile('45052.zip')
    layers = sorted(scan.namelist())

    imgdata = StringIO(scan.read(layers[layer]))
    slide = ImageZoom(imgdata)
    dz = DeepZoomGenerator(slide, overlap=0)

    if z is None:
        maxZoom = (dz.level_count - 8) - 1
        nLayers = len(layers)
        return render_template('viewer.html', maxZoom=maxZoom, nLayers=nLayers)

    try:
        tile = dz.get_tile(z + 8, (x, y))
    except ValueError:
        abort(404)

    response = StringIO()
    tile.save(response, "PNG", optimize=1)
    return response.getvalue(), 200, { 'Content-Type': 'image/png' }

if __name__ == '__main__':
    app.debug = True
    app.run()

