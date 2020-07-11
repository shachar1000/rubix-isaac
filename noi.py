import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d, Delaunay
import matplotlib.pyplot as plt
import pprint

points = np.random.rand(1000, 2)

# fucking stupid ass  donkey shit way to find circumcenter of triangle....   And this shit will be in bagrut FFS
def triangle_csc(pts):
    # diffs = x2-x1 and y2-y1 for 2 vertices of the triangle
    diffs = np.diff(pts[:3], axis=0) # the :3 is because we want only 2 vertices and not 3 for the calculations
    slopes = [(diffs[i][1]/diffs[i][0]) for i in range(2)]
    means = [[(pts[i][0]+pts[i+1][0])/2, (pts[i][1]+pts[i+1][1])/2] for i in range(2)]
    slopesOfPerpendicularBisectors = [(-1)/slopes[i] for i in range(len(slopes))]
    #y=mx+b   =>    b=y-mx
    b = [means[i][1]-(slopesOfPerpendicularBisectors[i]*means[i][0]) for i in range(2)]
    # m1x+b=m2x+b
    x = ((b[1]-b[0])/(slopesOfPerpendicularBisectors[0]-slopesOfPerpendicularBisectors[1]))
    y = (x*slopesOfPerpendicularBisectors[0])+b[0]
    return (x, y)

points = np.append(points, [[999,999], [-999,999], [999,-999], [-999,-999]], axis = 0)
delauny = Delaunay(points)
triangles = delauny.points[delauny.vertices]
circum_centers = np.array([triangle_csc(tri) for tri in triangles])



circum_centers = circum_centers[np.logical_not(np.isnan(circum_centers))]
circum_centers = np.split(circum_centers, len(circum_centers)/2)


vor = Voronoi(circum_centers)

# plot


polygons = []
# colorize
for region in vor.regions:
    if not -1 in region:
        polygon = [vor.vertices[i] for i in region]
        polygons.append(polygon)
    
# def centroids(polys):
#     # n sides of all polygons
#     #polys = np.array([np.array([np.array(polys[i][j]) for j in range(len(polys[i]))]) for i in range(len(polys))])
# 
#     # ok, so in python we have a list of polygons and every polygon is a list of points
#     # we need to convert from python to numpy 
# 
#     polys = polys[1:]
#     polys = np.array(polys)
#     polys = np.array([np.array(polys[i]) for i in range(len(polys))])
#     polys = np.array([np.array(np.array([value for value in polys[i]])) for i in range(len(polys))])
#     #pprint.pprint(polys)
#     lengths = [polys[i].shape[0] for i in range(len(polys))]
#     sumX = [np.sum([polys[i][:, 0]]) for i in range(len(polys))]
#     sumY = [np.sum([polys[i][:, 1]]) for i in range(len(polys))]
#     centroids = [(sumX[i]/lengths[i], sumY[i]/lengths[i]) for i  in range(len(polys))]
#     return centroids
    
    
def centroidsFunc(polys):
    polys = polys[1:]
    centroids = []
    for i in range(len(polys)):
        sumXY = [sum(point[coor] for point in polys[i]) for coor in [0, 1]]
        centroids.append([sumXY[coor]/len(polys[i]) for coor in [0, 1]])
    
    
    return list(filter(lambda centroid: centroid[0] < 100 and centroid[0] > -100, centroids))
        
     

for i in range(3):
    vor = Voronoi(centroidsFunc(polygons))
    polygons = []
    for region in vor.regions:
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            polygons.append(polygon)
    
def display(vor):
    voronoi_plot_2d(vor, show_vertices=False, show_points=False)
    for region in vor.regions:
        if not -1 in region:
            polygon = [vor.vertices[i] for i in region]
            plt.fill(*zip(*polygon))
    # fix the range of axes
    plt.xlim([0,1]), plt.ylim([0,1])    
    plt.show()

display(vor)
