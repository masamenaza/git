"""
This module contains the instantiations of color mapping classes
"""

import colors
from matplotlib import verbose
from matplotlib import rcParams
from matplotlib.numerix import asarray
from numerix import nx
LUTSIZE = rcParams['image.lut']


_cool_data = {'red':   ((),()),
              'green': ((),()),
              'blue':  ((),())}
              
_bone_data = {'red':   ((0., 0., 0.),(1.0, 1.0, 1.0)),
              'green': ((0., 0., 0.),(1.0, 1.0, 1.0)),
              'blue':  ((0., 0., 0.),(1.0, 1.0, 1.0))}                  


_autumn_data = {'red':   ((0., 1.0, 1.0),(1.0, 1.0, 1.0)),
                'green': ((0., 0., 0.),(1.0, 1.0, 1.0)),
                'blue':  ((0., 0., 0.),(1.0, 0., 0.))}                  
        
_bone_data = {'red':   ((0., 0., 0.),(0.746032, 0.652778, 0.652778),(1.0, 1.0, 1.0)),
              'green': ((0., 0., 0.),(0.365079, 0.319444, 0.319444),
                        (0.746032, 0.777778, 0.777778),(1.0, 1.0, 1.0)),
              'blue':  ((0., 0., 0.),(0.365079, 0.444444, 0.444444),(1.0, 1.0, 1.0))}     

_cool_data = {'red':   ((0., 0., 0.), (1.0, 1.0, 1.0)),
              'green': ((0., 1., 1.), (1.0, 0.,  0.)),
              'blue':  ((0., 1., 1.), (1.0, 1.,  1.))}
              
_copper_data = {'red':   ((0., 0., 0.),(0.809524, 1.000000, 1.000000),(1.0, 1.0, 1.0)),
                'green': ((0., 0., 0.),(1.0, 0.7812, 0.7812)),
                'blue':  ((0., 0., 0.),(1.0, 0.4975, 0.4975))}                  

_flag_data = {'red':   ((0., 1., 1.),(0.015873, 1.000000, 1.000000),
                        (0.031746, 0.000000, 0.000000),(0.047619, 0.000000, 0.000000),
                        (0.063492, 1.000000, 1.000000),(0.079365, 1.000000, 1.000000),
                        (0.095238, 0.000000, 0.000000),(0.111111, 0.000000, 0.000000),
                        (0.126984, 1.000000, 1.000000),(0.142857, 1.000000, 1.000000),
                        (0.158730, 0.000000, 0.000000),(0.174603, 0.000000, 0.000000),
                        (0.190476, 1.000000, 1.000000),(0.206349, 1.000000, 1.000000),
                        (0.222222, 0.000000, 0.000000),(0.238095, 0.000000, 0.000000),
                        (0.253968, 1.000000, 1.000000),(0.269841, 1.000000, 1.000000),
                        (0.285714, 0.000000, 0.000000),(0.301587, 0.000000, 0.000000),
                        (0.317460, 1.000000, 1.000000),(0.333333, 1.000000, 1.000000),
                        (0.349206, 0.000000, 0.000000),(0.365079, 0.000000, 0.000000),
                        (0.380952, 1.000000, 1.000000),(0.396825, 1.000000, 1.000000),
                        (0.412698, 0.000000, 0.000000),(0.428571, 0.000000, 0.000000),
                        (0.444444, 1.000000, 1.000000),(0.460317, 1.000000, 1.000000),
                        (0.476190, 0.000000, 0.000000),(0.492063, 0.000000, 0.000000),
                        (0.507937, 1.000000, 1.000000),(0.523810, 1.000000, 1.000000),
                        (0.539683, 0.000000, 0.000000),(0.555556, 0.000000, 0.000000),
                        (0.571429, 1.000000, 1.000000),(0.587302, 1.000000, 1.000000),
                        (0.603175, 0.000000, 0.000000),(0.619048, 0.000000, 0.000000),
                        (0.634921, 1.000000, 1.000000),(0.650794, 1.000000, 1.000000),
                        (0.666667, 0.000000, 0.000000),(0.682540, 0.000000, 0.000000),
                        (0.698413, 1.000000, 1.000000),(0.714286, 1.000000, 1.000000),
                        (0.730159, 0.000000, 0.000000),(0.746032, 0.000000, 0.000000),
                        (0.761905, 1.000000, 1.000000),(0.777778, 1.000000, 1.000000),
                        (0.793651, 0.000000, 0.000000),(0.809524, 0.000000, 0.000000),
                        (0.825397, 1.000000, 1.000000),(0.841270, 1.000000, 1.000000),
                        (0.857143, 0.000000, 0.000000),(0.873016, 0.000000, 0.000000),
                        (0.888889, 1.000000, 1.000000),(0.904762, 1.000000, 1.000000),
                        (0.920635, 0.000000, 0.000000),(0.936508, 0.000000, 0.000000),
                        (0.952381, 1.000000, 1.000000),(0.968254, 1.000000, 1.000000),
                        (0.984127, 0.000000, 0.000000),(1.0, 0., 0.)),
              'green': ((0., 0., 0.),(0.015873, 1.000000, 1.000000),
                        (0.031746, 0.000000, 0.000000),(0.063492, 0.000000, 0.000000),
                        (0.079365, 1.000000, 1.000000),(0.095238, 0.000000, 0.000000),
                        (0.126984, 0.000000, 0.000000),(0.142857, 1.000000, 1.000000),
                        (0.158730, 0.000000, 0.000000),(0.190476, 0.000000, 0.000000),
                        (0.206349, 1.000000, 1.000000),(0.222222, 0.000000, 0.000000),
                        (0.253968, 0.000000, 0.000000),(0.269841, 1.000000, 1.000000),
                        (0.285714, 0.000000, 0.000000),(0.317460, 0.000000, 0.000000),
                        (0.333333, 1.000000, 1.000000),(0.349206, 0.000000, 0.000000),
                        (0.380952, 0.000000, 0.000000),(0.396825, 1.000000, 1.000000),
                        (0.412698, 0.000000, 0.000000),(0.444444, 0.000000, 0.000000),
                        (0.460317, 1.000000, 1.000000),(0.476190, 0.000000, 0.000000),
                        (0.507937, 0.000000, 0.000000),(0.523810, 1.000000, 1.000000),
                        (0.539683, 0.000000, 0.000000),(0.571429, 0.000000, 0.000000),
                        (0.587302, 1.000000, 1.000000),(0.603175, 0.000000, 0.000000),
                        (0.634921, 0.000000, 0.000000),(0.650794, 1.000000, 1.000000),
                        (0.666667, 0.000000, 0.000000),(0.698413, 0.000000, 0.000000),
                        (0.714286, 1.000000, 1.000000),(0.730159, 0.000000, 0.000000),
                        (0.761905, 0.000000, 0.000000),(0.777778, 1.000000, 1.000000),
                        (0.793651, 0.000000, 0.000000),(0.825397, 0.000000, 0.000000),
                        (0.841270, 1.000000, 1.000000),(0.857143, 0.000000, 0.000000),
                        (0.888889, 0.000000, 0.000000),(0.904762, 1.000000, 1.000000),
                        (0.920635, 0.000000, 0.000000),(0.952381, 0.000000, 0.000000),
                        (0.968254, 1.000000, 1.000000),(0.984127, 0.000000, 0.000000),
                        (1.0, 0., 0.)),
              'blue':  ((0., 0., 0.),(0.015873, 1.000000, 1.000000),
                        (0.031746, 1.000000, 1.000000),(0.047619, 0.000000, 0.000000),
                        (0.063492, 0.000000, 0.000000),(0.079365, 1.000000, 1.000000),
                        (0.095238, 1.000000, 1.000000),(0.111111, 0.000000, 0.000000),
                        (0.126984, 0.000000, 0.000000),(0.142857, 1.000000, 1.000000),
                        (0.158730, 1.000000, 1.000000),(0.174603, 0.000000, 0.000000),
                        (0.190476, 0.000000, 0.000000),(0.206349, 1.000000, 1.000000),
                        (0.222222, 1.000000, 1.000000),(0.238095, 0.000000, 0.000000),
                        (0.253968, 0.000000, 0.000000),(0.269841, 1.000000, 1.000000),
                        (0.285714, 1.000000, 1.000000),(0.301587, 0.000000, 0.000000),
                        (0.317460, 0.000000, 0.000000),(0.333333, 1.000000, 1.000000),
                        (0.349206, 1.000000, 1.000000),(0.365079, 0.000000, 0.000000),
                        (0.380952, 0.000000, 0.000000),(0.396825, 1.000000, 1.000000),
                        (0.412698, 1.000000, 1.000000),(0.428571, 0.000000, 0.000000),
                        (0.444444, 0.000000, 0.000000),(0.460317, 1.000000, 1.000000),
                        (0.476190, 1.000000, 1.000000),(0.492063, 0.000000, 0.000000),
                        (0.507937, 0.000000, 0.000000),(0.523810, 1.000000, 1.000000),
                        (0.539683, 1.000000, 1.000000),(0.555556, 0.000000, 0.000000),
                        (0.571429, 0.000000, 0.000000),(0.587302, 1.000000, 1.000000),
                        (0.603175, 1.000000, 1.000000),(0.619048, 0.000000, 0.000000),
                        (0.634921, 0.000000, 0.000000),(0.650794, 1.000000, 1.000000),
                        (0.666667, 1.000000, 1.000000),(0.682540, 0.000000, 0.000000),
                        (0.698413, 0.000000, 0.000000),(0.714286, 1.000000, 1.000000),
                        (0.730159, 1.000000, 1.000000),(0.746032, 0.000000, 0.000000),
                        (0.761905, 0.000000, 0.000000),(0.777778, 1.000000, 1.000000),
                        (0.793651, 1.000000, 1.000000),(0.809524, 0.000000, 0.000000),
                        (0.825397, 0.000000, 0.000000),(0.841270, 1.000000, 1.000000),
                        (0.857143, 1.000000, 1.000000),(0.873016, 0.000000, 0.000000),
                        (0.888889, 0.000000, 0.000000),(0.904762, 1.000000, 1.000000),
                        (0.920635, 1.000000, 1.000000),(0.936508, 0.000000, 0.000000),
                        (0.952381, 0.000000, 0.000000),(0.968254, 1.000000, 1.000000),
                        (0.984127, 1.000000, 1.000000),(1.0, 0., 0.))}  
                        
_gray_data =  {'red':   ((0., 0, 0), (1., 1, 1)),
               'green': ((0., 0, 0), (1., 1, 1)),
               'blue':  ((0., 0, 0), (1., 1, 1))}      

_hot_data = {'red':   ((0., 0.0416, 0.0416),(0.365079, 1.000000, 1.000000),(1.0, 1.0, 1.0)),
             'green': ((0., 0., 0.),(0.365079, 0.000000, 0.000000),
                       (0.746032, 1.000000, 1.000000),(1.0, 1.0, 1.0)),
             'blue':  ((0., 0., 0.),(0.746032, 0.000000, 0.000000),(1.0, 1.0, 1.0))}                  

_hsv_data = {'red':   ((0., 1., 1.),(0.158730, 1.000000, 1.000000),
                       (0.174603, 0.968750, 0.968750),(0.333333, 0.031250, 0.031250),
                       (0.349206, 0.000000, 0.000000),(0.666667, 0.000000, 0.000000),
                       (0.682540, 0.031250, 0.031250),(0.841270, 0.968750, 0.968750),
                       (0.857143, 1.000000, 1.000000),(1.0, 1.0, 1.0)),
             'green': ((0., 0., 0.),(0.158730, 0.937500, 0.937500),
                       (0.174603, 1.000000, 1.000000),(0.507937, 1.000000, 1.000000),
                       (0.666667, 0.062500, 0.062500),(0.682540, 0.000000, 0.000000),
                       (1.0, 0., 0.)),
             'blue':  ((0., 0., 0.),(0.333333, 0.000000, 0.000000),
                       (0.349206, 0.062500, 0.062500),(0.507937, 1.000000, 1.000000),
                       (0.841270, 1.000000, 1.000000),(0.857143, 0.937500, 0.937500),
                       (1.0, 0.09375, 0.09375))} 
                          
_jet_data =   {'red':   ((0., 0, 0), (0.35, 0, 0), (0.66, 1, 1), (0.89,1, 1), 
                         (1, 0.5, 0.5)),
               'green': ((0., 0, 0), (0.125,0, 0), (0.375,1, 1), (0.64,1, 1),
                         (0.91,0,0), (1, 0, 0)),   
               'blue':  ((0., 0.5, 0.5), (0.11, 1, 1), (0.34, 1, 1), (0.65,0, 0),
                         (1, 0, 0))}
                   
_pink_data = {'red':   ((0., 0.1178, 0.1178),(0.015873, 0.195857, 0.195857),
                        (0.031746, 0.250661, 0.250661),(0.047619, 0.295468, 0.295468),
                        (0.063492, 0.334324, 0.334324),(0.079365, 0.369112, 0.369112),
                        (0.095238, 0.400892, 0.400892),(0.111111, 0.430331, 0.430331),
                        (0.126984, 0.457882, 0.457882),(0.142857, 0.483867, 0.483867),
                        (0.158730, 0.508525, 0.508525),(0.174603, 0.532042, 0.532042),
                        (0.190476, 0.554563, 0.554563),(0.206349, 0.576204, 0.576204),
                        (0.222222, 0.597061, 0.597061),(0.238095, 0.617213, 0.617213),
                        (0.253968, 0.636729, 0.636729),(0.269841, 0.655663, 0.655663),
                        (0.285714, 0.674066, 0.674066),(0.301587, 0.691980, 0.691980),
                        (0.317460, 0.709441, 0.709441),(0.333333, 0.726483, 0.726483),
                        (0.349206, 0.743134, 0.743134),(0.365079, 0.759421, 0.759421),
                        (0.380952, 0.766356, 0.766356),(0.396825, 0.773229, 0.773229),
                        (0.412698, 0.780042, 0.780042),(0.428571, 0.786796, 0.786796),
                        (0.444444, 0.793492, 0.793492),(0.460317, 0.800132, 0.800132),
                        (0.476190, 0.806718, 0.806718),(0.492063, 0.813250, 0.813250),
                        (0.507937, 0.819730, 0.819730),(0.523810, 0.826160, 0.826160),
                        (0.539683, 0.832539, 0.832539),(0.555556, 0.838870, 0.838870),
                        (0.571429, 0.845154, 0.845154),(0.587302, 0.851392, 0.851392),
                        (0.603175, 0.857584, 0.857584),(0.619048, 0.863731, 0.863731),
                        (0.634921, 0.869835, 0.869835),(0.650794, 0.875897, 0.875897),
                        (0.666667, 0.881917, 0.881917),(0.682540, 0.887896, 0.887896),
                        (0.698413, 0.893835, 0.893835),(0.714286, 0.899735, 0.899735),
                        (0.730159, 0.905597, 0.905597),(0.746032, 0.911421, 0.911421),
                        (0.761905, 0.917208, 0.917208),(0.777778, 0.922958, 0.922958),
                        (0.793651, 0.928673, 0.928673),(0.809524, 0.934353, 0.934353),
                        (0.825397, 0.939999, 0.939999),(0.841270, 0.945611, 0.945611),
                        (0.857143, 0.951190, 0.951190),(0.873016, 0.956736, 0.956736),
                        (0.888889, 0.962250, 0.962250),(0.904762, 0.967733, 0.967733),
                        (0.920635, 0.973185, 0.973185),(0.936508, 0.978607, 0.978607),
                        (0.952381, 0.983999, 0.983999),(0.968254, 0.989361, 0.989361),
                        (0.984127, 0.994695, 0.994695),(1.0, 1.0, 1.0)),
              'green': ((0., 0., 0.),(0.015873, 0.102869, 0.102869),
                        (0.031746, 0.145479, 0.145479),(0.047619, 0.178174, 0.178174),
                        (0.063492, 0.205738, 0.205738),(0.079365, 0.230022, 0.230022),
                        (0.095238, 0.251976, 0.251976),(0.111111, 0.272166, 0.272166),
                        (0.126984, 0.290957, 0.290957),(0.142857, 0.308607, 0.308607),
                        (0.158730, 0.325300, 0.325300),(0.174603, 0.341178, 0.341178),
                        (0.190476, 0.356348, 0.356348),(0.206349, 0.370899, 0.370899),
                        (0.222222, 0.384900, 0.384900),(0.238095, 0.398410, 0.398410),
                        (0.253968, 0.411476, 0.411476),(0.269841, 0.424139, 0.424139),
                        (0.285714, 0.436436, 0.436436),(0.301587, 0.448395, 0.448395),
                        (0.317460, 0.460044, 0.460044),(0.333333, 0.471405, 0.471405),
                        (0.349206, 0.482498, 0.482498),(0.365079, 0.493342, 0.493342),
                        (0.380952, 0.517549, 0.517549),(0.396825, 0.540674, 0.540674),
                        (0.412698, 0.562849, 0.562849),(0.428571, 0.584183, 0.584183),
                        (0.444444, 0.604765, 0.604765),(0.460317, 0.624669, 0.624669),
                        (0.476190, 0.643958, 0.643958),(0.492063, 0.662687, 0.662687),
                        (0.507937, 0.680900, 0.680900),(0.523810, 0.698638, 0.698638),
                        (0.539683, 0.715937, 0.715937),(0.555556, 0.732828, 0.732828),
                        (0.571429, 0.749338, 0.749338),(0.587302, 0.765493, 0.765493),
                        (0.603175, 0.781313, 0.781313),(0.619048, 0.796819, 0.796819),
                        (0.634921, 0.812029, 0.812029),(0.650794, 0.826960, 0.826960),
                        (0.666667, 0.841625, 0.841625),(0.682540, 0.856040, 0.856040),
                        (0.698413, 0.870216, 0.870216),(0.714286, 0.884164, 0.884164),
                        (0.730159, 0.897896, 0.897896),(0.746032, 0.911421, 0.911421),
                        (0.761905, 0.917208, 0.917208),(0.777778, 0.922958, 0.922958),
                        (0.793651, 0.928673, 0.928673),(0.809524, 0.934353, 0.934353),
                        (0.825397, 0.939999, 0.939999),(0.841270, 0.945611, 0.945611),
                        (0.857143, 0.951190, 0.951190),(0.873016, 0.956736, 0.956736),
                        (0.888889, 0.962250, 0.962250),(0.904762, 0.967733, 0.967733),
                        (0.920635, 0.973185, 0.973185),(0.936508, 0.978607, 0.978607),
                        (0.952381, 0.983999, 0.983999),(0.968254, 0.989361, 0.989361),
                        (0.984127, 0.994695, 0.994695),(1.0, 1.0, 1.0)),
              'blue':  ((0., 0., 0.),(0.015873, 0.102869, 0.102869),
                        (0.031746, 0.145479, 0.145479),(0.047619, 0.178174, 0.178174),
                        (0.063492, 0.205738, 0.205738),(0.079365, 0.230022, 0.230022),
                        (0.095238, 0.251976, 0.251976),(0.111111, 0.272166, 0.272166),
                        (0.126984, 0.290957, 0.290957),(0.142857, 0.308607, 0.308607),
                        (0.158730, 0.325300, 0.325300),(0.174603, 0.341178, 0.341178),
                        (0.190476, 0.356348, 0.356348),(0.206349, 0.370899, 0.370899),
                        (0.222222, 0.384900, 0.384900),(0.238095, 0.398410, 0.398410),
                        (0.253968, 0.411476, 0.411476),(0.269841, 0.424139, 0.424139),
                        (0.285714, 0.436436, 0.436436),(0.301587, 0.448395, 0.448395),
                        (0.317460, 0.460044, 0.460044),(0.333333, 0.471405, 0.471405),
                        (0.349206, 0.482498, 0.482498),(0.365079, 0.493342, 0.493342),
                        (0.380952, 0.503953, 0.503953),(0.396825, 0.514344, 0.514344),
                        (0.412698, 0.524531, 0.524531),(0.428571, 0.534522, 0.534522),
                        (0.444444, 0.544331, 0.544331),(0.460317, 0.553966, 0.553966),
                        (0.476190, 0.563436, 0.563436),(0.492063, 0.572750, 0.572750),
                        (0.507937, 0.581914, 0.581914),(0.523810, 0.590937, 0.590937),
                        (0.539683, 0.599824, 0.599824),(0.555556, 0.608581, 0.608581),
                        (0.571429, 0.617213, 0.617213),(0.587302, 0.625727, 0.625727),
                        (0.603175, 0.634126, 0.634126),(0.619048, 0.642416, 0.642416),
                        (0.634921, 0.650600, 0.650600),(0.650794, 0.658682, 0.658682),
                        (0.666667, 0.666667, 0.666667),(0.682540, 0.674556, 0.674556),
                        (0.698413, 0.682355, 0.682355),(0.714286, 0.690066, 0.690066),
                        (0.730159, 0.697691, 0.697691),(0.746032, 0.705234, 0.705234),
                        (0.761905, 0.727166, 0.727166),(0.777778, 0.748455, 0.748455),
                        (0.793651, 0.769156, 0.769156),(0.809524, 0.789314, 0.789314),
                        (0.825397, 0.808969, 0.808969),(0.841270, 0.828159, 0.828159),
                        (0.857143, 0.846913, 0.846913),(0.873016, 0.865261, 0.865261),
                        (0.888889, 0.883229, 0.883229),(0.904762, 0.900837, 0.900837),
                        (0.920635, 0.918109, 0.918109),(0.936508, 0.935061, 0.935061),
                        (0.952381, 0.951711, 0.951711),(0.968254, 0.968075, 0.968075),
                        (0.984127, 0.984167, 0.984167),(1.0, 1.0, 1.0))}                  
 
_prism_data = {'red':   ((0., 1., 1.),(0.031746, 1.000000, 1.000000),
                         (0.047619, 0.000000, 0.000000),(0.063492, 0.000000, 0.000000),
                         (0.079365, 0.666667, 0.666667),(0.095238, 1.000000, 1.000000),
                         (0.126984, 1.000000, 1.000000),(0.142857, 0.000000, 0.000000),
                         (0.158730, 0.000000, 0.000000),(0.174603, 0.666667, 0.666667),
                         (0.190476, 1.000000, 1.000000),(0.222222, 1.000000, 1.000000),
                         (0.238095, 0.000000, 0.000000),(0.253968, 0.000000, 0.000000),
                         (0.269841, 0.666667, 0.666667),(0.285714, 1.000000, 1.000000),
                         (0.317460, 1.000000, 1.000000),(0.333333, 0.000000, 0.000000),
                         (0.349206, 0.000000, 0.000000),(0.365079, 0.666667, 0.666667),
                         (0.380952, 1.000000, 1.000000),(0.412698, 1.000000, 1.000000),
                         (0.428571, 0.000000, 0.000000),(0.444444, 0.000000, 0.000000),
                         (0.460317, 0.666667, 0.666667),(0.476190, 1.000000, 1.000000),
                         (0.507937, 1.000000, 1.000000),(0.523810, 0.000000, 0.000000),
                         (0.539683, 0.000000, 0.000000),(0.555556, 0.666667, 0.666667),
                         (0.571429, 1.000000, 1.000000),(0.603175, 1.000000, 1.000000),
                         (0.619048, 0.000000, 0.000000),(0.634921, 0.000000, 0.000000),
                         (0.650794, 0.666667, 0.666667),(0.666667, 1.000000, 1.000000),
                         (0.698413, 1.000000, 1.000000),(0.714286, 0.000000, 0.000000),
                         (0.730159, 0.000000, 0.000000),(0.746032, 0.666667, 0.666667),
                         (0.761905, 1.000000, 1.000000),(0.793651, 1.000000, 1.000000),
                         (0.809524, 0.000000, 0.000000),(0.825397, 0.000000, 0.000000),
                         (0.841270, 0.666667, 0.666667),(0.857143, 1.000000, 1.000000),
                         (0.888889, 1.000000, 1.000000),(0.904762, 0.000000, 0.000000),      
                         (0.920635, 0.000000, 0.000000),(0.936508, 0.666667, 0.666667),
                         (0.952381, 1.000000, 1.000000),(0.984127, 1.000000, 1.000000),
                         (1.0, 0.0, 0.0)),
               'green': ((0., 0., 0.),(0.031746, 1.000000, 1.000000),
                         (0.047619, 1.000000, 1.000000),(0.063492, 0.000000, 0.000000),
                         (0.095238, 0.000000, 0.000000),(0.126984, 1.000000, 1.000000),
                         (0.142857, 1.000000, 1.000000),(0.158730, 0.000000, 0.000000),
                         (0.190476, 0.000000, 0.000000),(0.222222, 1.000000, 1.000000),
                         (0.238095, 1.000000, 1.000000),(0.253968, 0.000000, 0.000000),
                         (0.285714, 0.000000, 0.000000),(0.317460, 1.000000, 1.000000),
                         (0.333333, 1.000000, 1.000000),(0.349206, 0.000000, 0.000000),
                         (0.380952, 0.000000, 0.000000),(0.412698, 1.000000, 1.000000),
                         (0.428571, 1.000000, 1.000000),(0.444444, 0.000000, 0.000000),
                         (0.476190, 0.000000, 0.000000),(0.507937, 1.000000, 1.000000),
                         (0.523810, 1.000000, 1.000000),(0.539683, 0.000000, 0.000000),
                         (0.571429, 0.000000, 0.000000),(0.603175, 1.000000, 1.000000),
                         (0.619048, 1.000000, 1.000000),(0.634921, 0.000000, 0.000000),
                         (0.666667, 0.000000, 0.000000),(0.698413, 1.000000, 1.000000),
                         (0.714286, 1.000000, 1.000000),(0.730159, 0.000000, 0.000000),
                         (0.761905, 0.000000, 0.000000),(0.793651, 1.000000, 1.000000),
                         (0.809524, 1.000000, 1.000000),(0.825397, 0.000000, 0.000000),
                         (0.857143, 0.000000, 0.000000),(0.888889, 1.000000, 1.000000),
                         (0.904762, 1.000000, 1.000000),(0.920635, 0.000000, 0.000000),
                         (0.952381, 0.000000, 0.000000),(0.984127, 1.000000, 1.000000),
                         (1.0, 1.0, 1.0)),
               'blue':  ((0., 0., 0.),(0.047619, 0.000000, 0.000000),
                         (0.063492, 1.000000, 1.000000),(0.079365, 1.000000, 1.000000),
                         (0.095238, 0.000000, 0.000000),(0.142857, 0.000000, 0.000000),
                         (0.158730, 1.000000, 1.000000),(0.174603, 1.000000, 1.000000),
                         (0.190476, 0.000000, 0.000000),(0.238095, 0.000000, 0.000000),
                         (0.253968, 1.000000, 1.000000),(0.269841, 1.000000, 1.000000),
                         (0.285714, 0.000000, 0.000000),(0.333333, 0.000000, 0.000000),
                         (0.349206, 1.000000, 1.000000),(0.365079, 1.000000, 1.000000),
                         (0.380952, 0.000000, 0.000000),(0.428571, 0.000000, 0.000000),
                         (0.444444, 1.000000, 1.000000),(0.460317, 1.000000, 1.000000),
                         (0.476190, 0.000000, 0.000000),(0.523810, 0.000000, 0.000000),
                         (0.539683, 1.000000, 1.000000),(0.555556, 1.000000, 1.000000),
                         (0.571429, 0.000000, 0.000000),(0.619048, 0.000000, 0.000000),
                         (0.634921, 1.000000, 1.000000),(0.650794, 1.000000, 1.000000),
                         (0.666667, 0.000000, 0.000000),(0.714286, 0.000000, 0.000000),
                         (0.730159, 1.000000, 1.000000),(0.746032, 1.000000, 1.000000),
                         (0.761905, 0.000000, 0.000000),(0.809524, 0.000000, 0.000000),
                         (0.825397, 1.000000, 1.000000),(0.841270, 1.000000, 1.000000),
                         (0.857143, 0.000000, 0.000000),(0.904762, 0.000000, 0.000000),
                         (0.920635, 1.000000, 1.000000),(0.936508, 1.000000, 1.000000),
                         (0.952381, 0.000000, 0.000000),(1.0, 0.0, 0.0))}                  

_spring_data = {'red':   ((0., 1., 1.),(1.0, 1.0, 1.0)),
                'green': ((0., 0., 0.),(1.0, 1.0, 1.0)),
                'blue':  ((0., 1., 1.),(1.0, 0.0, 0.0))}                  


_summer_data = {'red':   ((0., 0., 0.),(1.0, 1.0, 1.0)),
                'green': ((0., 0.5, 0.5),(1.0, 1.0, 1.0)),
                'blue':  ((0., 0.4, 0.4),(1.0, 0.4, 0.4))}                  


_winter_data = {'red':   ((0., 0., 0.),(1.0, 0.0, 0.0)),
                'green': ((0., 0., 0.),(1.0, 1.0, 1.0)),
                'blue':  ((0., 1., 1.),(1.0, 0.5, 0.5))}                  

autumn = colors.LinearSegmentedColormap('autumn', _autumn_data, LUTSIZE)
bone   = colors.LinearSegmentedColormap('bone  ', _bone_data, LUTSIZE)
cool   = colors.LinearSegmentedColormap('cool',   _cool_data, LUTSIZE)
copper = colors.LinearSegmentedColormap('copper', _copper_data, LUTSIZE)
flag   = colors.LinearSegmentedColormap('flag',   _flag_data, LUTSIZE)
gray   = colors.LinearSegmentedColormap('gray',   _gray_data, LUTSIZE)
hot    = colors.LinearSegmentedColormap('hot',    _hot_data, LUTSIZE)
hsv    = colors.LinearSegmentedColormap('hsv',    _hsv_data, LUTSIZE)
jet    = colors.LinearSegmentedColormap('jet',    _jet_data, LUTSIZE)
pink   = colors.LinearSegmentedColormap('pink',   _pink_data, LUTSIZE)
prism  = colors.LinearSegmentedColormap('prism',  _prism_data, LUTSIZE)
spring = colors.LinearSegmentedColormap('spring', _spring_data, LUTSIZE)
summer = colors.LinearSegmentedColormap('summer', _summer_data, LUTSIZE)
winter = colors.LinearSegmentedColormap('winter', _winter_data, LUTSIZE)




datad = {
    'autumn': _autumn_data,
    'bone':   _bone_data,
    'cool':   _cool_data,
    'copper': _copper_data,
    'flag':   _flag_data,
    'gray' :  _gray_data,
    'hot':    _hot_data,
    'hsv':    _hsv_data,
    'jet' :   _jet_data,
    'pink':   _pink_data,
    'prism':  _prism_data,
    'spring': _spring_data,
    'summer': _summer_data,
    'winter': _winter_data
    }


def get_cmap(name=None, lut=None):
    """
    Get a colormap instance, defaulting to rc values if name is None
    """
    if name is None: name = rcParams['image.cmap']
    if lut is None: lut = rcParams['image.lut']
    
    assert(name in datad.keys())
    return colors.LinearSegmentedColormap(name,  datad[name], lut)

# These are provided for backwards compat
import sys


class ScalarMappable:    
    """
    This is a mixin class to support scalar -> RGBA mapping.  Handles
    normalization and colormapping
    """

    def __init__(self, norm=None, cmap=None):    
        """
        norm is a colors.Norm instance to map luminance to 0-1
        cmap is a cm colormap instance
        """

        if cmap is None: cmap = get_cmap()        
        if norm is None: norm = colors.normalize()

        self._A = None
        self.norm = norm
        self.cmap = cmap
        self.observers = []
        self.colorbar = None

    def set_colorbar(self, im, ax):
        'set the colorbar image and axes associated with mappable'
        self.colorbar = im, ax

    def to_rgba(self, x, alpha=1.0):
        # assume normalized rgb, rgba
        x = asarray(x)
        if len(x.shape)>2: return x
        x = self.norm(x)
        return self.cmap(x, alpha)
    
    def set_array(self, A):
        'Set the image array from numeric/numarray A'
        self._A = A.astype(nx.Float32)

    def set_clim(self, vmin=None, vmax=None):
        'set the norm limits for image scaling'
        self.norm.vmin = vmin
        self.norm.vmax = vmax
        if self.colorbar is not None:
            im, ax = self.colorbar
            ax.set_ylim((vmin, vmax))
        self.changed()
        
    def set_cmap(self, cmap):
        'set the colormap for luminance data'
        if cmap is None: cmap = get_cmap()                
        self.cmap = cmap
        self.changed()
        
    def set_norm(self, norm):
        'set the normalization instance'
        if norm is None: norm = colors.normalize()
        self.norm = norm
        self.changed()

    def autoscale(self):
        """
        Autoscale the scalar limits on the norm instance using the
        current array
        """
        if self._A is None:
            raise TypeError('You must first set_array for mappable')
        self.norm.autoscale(self._A)
        self.changed()
        
    def add_observer(self, mappable):
        """
        whenever the norm, clim or cmap is set, call the notify
        instance of the mappable observer with self.

        This is designed to allow one image to follow changes in the
        cmap of another image
        """
        self.observers.append(mappable)
        
    def notify(self, mappable):
        """
        If this is called then we are pegged to another mappable.
        Update the cmap, norm accordingly
        """
        self.set_cmap(mappable.cmap)
        self.set_norm(mappable.norm)

    def changed(self):
        """
        Call this whenever the mappable is changed so observers can
        update state
        """
        for observer in self.observers:
            observer.notify(self)
