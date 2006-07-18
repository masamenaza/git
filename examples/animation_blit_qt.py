# For detailed comments on animation and the techniqes used here, see
# the wiki entry http://www.scipy.org/Cookbook/Matplotlib/Animations

import os, sys
import matplotlib
matplotlib.use('QtAgg') # qt3 example

from qt import *
# Note: color-intensive applications may require a different color allocation
# strategy.
QApplication.setColorSpec(QApplication.NormalColor)

TRUE  = 1
FALSE = 0

import pylab as p
import matplotlib.numerix as nx
import time

class BlitQT(QObject):
    def __init__(self):
        QObject.__init__(self, None, "app")

        self.ax = p.subplot(111)
        self.canvas = self.ax.figure.canvas
        self.cnt = 0
        
        # create the initial line
        self.x = nx.arange(0,2*nx.pi,0.01)
        self.line, = p.plot(self.x, nx.sin(self.x), animated=True, lw=2)
        
        self.background = None
    
    def timerEvent(self, evt):
        if self.background is None:
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        
        # restore the clean slate background
        self.canvas.restore_region(self.background)
        # update the data
        self.line.set_ydata(nx.sin(self.x+self.cnt/10.0))  
        # just draw the animated artist
        self.ax.draw_artist(self.line)
        # just redraw the axes rectangle
        self.canvas.blit(self.ax.bbox) 
    
        if self.cnt==200:
            # print the timing info and quit
            print 'FPS:' , 200/(time.time()-self.tstart)
            sys.exit()

        else:
            self.cnt += 1
            
p.subplots_adjust(left=0.3, bottom=0.3) # check for flipy bugs
p.grid()

app = BlitQT()
# for profiling
app.tstart = time.time()
app.startTimer(0)

p.show()
