"""
The image module supports basic image loading, rescaling and display
operations.

"""
from __future__ import division
import sys, os
from matplotlib import rcParams
from artist import Artist
from colors import normalize, colorConverter
import cm
from numerix import arange
import _image



class AxesImage(Artist, cm.ScalarMappable):

    def __init__(self, ax,
                 cmap = None,
                 norm = None,
                 aspect=None,
                 interpolation=None,
                 origin=None,
                 extent=None,
                 ):

        """
        aspect, interpolation and cmap default to their rc setting

        cmap is a cm colormap instance
        norm is a colors.normalize instance to map luminance to 0-1

        extent is a data xmin, xmax, ymin, ymax for making image plots
        registered with data plots.  Default is the image dimensions
        in pixels
        
        """
        Artist.__init__(self)        
        cm.ScalarMappable.__init__(self, norm, cmap)

        if origin is None: origin = rcParams['image.origin']
        self.origin = origin
        self._extent = extent      

        # map interpolation strings to module constants
        self._interpd = {
            'bicubic'     : _image.BICUBIC,
            'bilinear'    : _image.BILINEAR,
            'blackman100' : _image.BLACKMAN100,
            'blackman256' : _image.BLACKMAN256,
            'blackman64'  : _image.BLACKMAN64,
            'nearest'     : _image.NEAREST,
            'sinc144'     : _image.SINC144,
            'sinc256'     : _image.SINC256,
            'sinc64'      : _image.SINC64,
            'spline16'    : _image.SPLINE16,
            'spline36'    : _image.SPLINE36,       
        }

        # map aspect ratio strings to module constants
        self._aspectd = {
            'free'     : _image.ASPECT_FREE,
            'preserve' : _image.ASPECT_PRESERVE,
        }

        # reverse interp dict
        self._interpdr = dict([ (v,k) for k,v in self._interpd.items()])

        # reverse aspect dict
        self._aspectdr = dict([ (v,k) for k,v in self._aspectd.items()])

        if aspect is None: aspect = rcParams['image.aspect']
        if interpolation is None: interpolation = rcParams['image.interpolation']        
        
        self.set_interpolation(interpolation)
        self.set_aspect( aspect)
        self.axes = ax

        
    def get_size(self):
        'Get the numrows, numcols of the input image'
        if self._A is None:
            raise RuntimeError('You must first set the image array')

        return self._A.shape[:2]

    def make_image(self, flipy):        

        if self._A is not None:
            x = self.to_rgba(self._A, self._alpha)
            im = _image.fromarray(x, 0)
        else:
            raise RuntimeError('You must first set the image array or the image attribute')

        bg = colorConverter.to_rgba(self.axes.get_frame().get_facecolor(), 0)
        im.set_bg( *bg)
        im.is_grayscale = (self.cmap.name == "gray" and
                           len(self._A.shape) == 2)
        
        im.set_aspect(self._aspectd[self._aspect])        
        im.set_interpolation(self._interpd[self._interpolation])



        # image input dimensions
        numrows, numcols = im.get_size()
        im.reset_matrix()

        xmin, xmax, ymin, ymax = self.get_extent() 
        dxintv = xmax-xmin
        dyintv = ymax-ymin

        # the viewport scale factor
        sx = dxintv/self.axes.viewLim.width()
        sy = dyintv/self.axes.viewLim.height()

        if im.get_interpolation()!=_image.NEAREST:
            im.apply_translation(-1, -1)

        # the viewport translation
        tx = (xmin-self.axes.viewLim.xmin())/dxintv * numcols
        if flipy: 
            ty = -(ymax-self.axes.viewLim.ymax())/dyintv * numrows
        else:
            ty = (ymin-self.axes.viewLim.ymin())/dyintv * numrows

        l, b, widthDisplay, heightDisplay = self.axes.bbox.get_bounds()

        im.apply_translation(tx, ty)
        im.apply_scaling(sx, sy)

        # resize viewport to display
        rx = widthDisplay / numcols
        ry = heightDisplay  / numrows

        if im.get_aspect()==_image.ASPECT_PRESERVE:
            if ry < rx: rx = ry
            # todo: center the image in viewport
            im.apply_scaling(rx, rx)
        else:
            im.apply_scaling(rx, ry)

        #print tx, ty, sx, sy, rx, ry, widthDisplay, heightDisplay
        im.resize(int(widthDisplay+0.5), int(heightDisplay+0.5))
        return im
    
    def draw(self, renderer, *args, **kwargs):
        isUpper = self.origin=='upper'
        flipy = renderer.flipy()

        im = self.make_image(isUpper)
        l, b, widthDisplay, heightDisplay = self.axes.bbox.get_bounds()
        if isUpper:
            #offset is distance from top of figure
            oy = self.axes.figure.bbox.height()-(b+heightDisplay)
            renderer.draw_image(l, oy, im, self.origin, self.axes.bbox)
        else:
            # compute the location of the origin
            oy = b
            renderer.draw_image(l, oy, im, self.origin, self.axes.bbox)

    def write_png(self, fname):
        """Write the image to png file with fname"""
        im = self.make_image(False)
        im.write_png(fname)
        

    def set_array(self, A):
        'Set the image array from numeric/numarray A'
        cm.ScalarMappable.set_array(self, A)


    def get_aspect(self):
        """
        Return the method used to constrain the aspoect ratio of the
        One of
        
        'free'     : aspect ratio not constrained
        'preserve' : preserve aspect ratio when resizing
        """
        return self._aspect



    def get_interpolation(self):
        """
        Return the interpolation method the image uses when resizing.

        One of
        
        'bicubic', 'bilinear', 'blackman100', 'blackman256', 'blackman64',
        'nearest', 'sinc144', 'sinc256', 'sinc64', 'spline16', 'spline36'
        """
        return self._interpolation

    def set_aspect(self, s):
        """
        Set the method used to constrain the aspoect ratio of the
        image ehen resizing,

        One of
        
        'free'     : aspect ratio not constrained
        'preserve' : preserve aspect ratio when resizing
        """

        s = s.lower()
        if not self._aspectd.has_key(s):
            raise ValueError('Illegal aspect string')
        self._aspect = s


    def set_interpolation(self, s):
        """
        Set the interpolation method the image uses when resizing.

        One of
        
        'bicubic', 'bilinear', 'blackman100', 'blackman256', 'blackman64',
        'nearest', 'sinc144', 'sinc256', 'sinc64', 'spline16', 'spline36'
        """
        
        s = s.lower()
        if not self._interpd.has_key(s):
            raise ValueError('Illegal interpolation string')
        self._interpolation = s



    def set_data_extent(self, xmin, xmax, ymin, ymax):
        """
        Set the data extent that the image pixels represent.  If you
        are using the matlab interface, use Axes.set_image_extent
        instead
        """
        print >>sys.stderr, 'set_data_extent deprecated; please pass extent in imshow constructor'
        sys.exit()

        
    def get_extent(self):
        'get the image extent: xmin, xmax, ymin, ymax'
        if self._extent is not None:
            return self._extent
        else:
            numrows, numcols = self.get_size()
            width, height = numcols, numrows
            return 0, width, 0, height


class FigureImage(Artist, cm.ScalarMappable):
    def __init__(self, fig,
                 cmap = None,
                 norm = None,
                 offsetx = 0,
                 offsety = 0,
                 origin=None,
                 ):

        """
        cmap is a cm colormap instance
        norm is a colors.normalize instance to map luminance to 0-1
        
        """
        Artist.__init__(self)
        cm.ScalarMappable.__init__(self, norm, cmap)
        if origin is None: origin = rcParams['image.origin']
        self.origin = origin
        self.figure = fig
        self.ox = offsetx
        self.oy = offsety
        

    def get_size(self):
        'Get the numrows, numcols of the input image'
        if self._A is None:
            raise RuntimeError('You must first set the image array')

        return self._A.shape[:2]

    def make_image(self):        
        if self._A is None:
            raise RuntimeError('You must first set the image array')
        
        x = self.to_rgba(self._A, self._alpha)

        im = _image.fromarray(x, 1)
        im.set_bg( *colorConverter.to_rgba(self.figure.get_facecolor(), 0) )        
        im.is_grayscale = (self.cmap.name == "gray" and
                           len(self._A.shape) == 2)
        return im
    
    def draw(self, renderer, *args, **kwargs):
        im = self.make_image()
        renderer.draw_image(self.ox, self.oy, im, self.origin, self.figure.bbox)

    def write_png(self, fname):
        """Write the image to png file with fname"""
        im = self.make_image()
        im.write_png(fname)

def imread(fname):
    """
    return image file in fname as numerix array

    Return value is a MxNx4 array of 0-1 normalized floats

    """
    handlers = {'png' :_image.readpng,
                }
    basename, ext = os.path.splitext(fname)
    ext = ext.lower()[1:]
    if ext not in handlers.keys():
        raise ValueError('Only know how to handled extensions: %s' % ', '.handlers.keys())

    handler = handlers[ext]
    return handler(fname)

    
