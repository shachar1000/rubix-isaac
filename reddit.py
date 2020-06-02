import cv2
import numpy as np
import imutils
from scipy.spatial import distance as dist
from pynput import keyboard
import math
from functools import reduce
from operator import itemgetter

def detect(image, colors=None):
    
    
    
    original = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = np.zeros(image.shape, dtype=np.uint8)

    blurred= cv2.GaussianBlur(original, (5, 5), 0)
    lab_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB) # this is lab for means

    # image = cv2.bilateralFilter(image,9,75,75)
    # image = cv2.fastNlMeansDenoisingColored(image,None,10,10,7,21)
    # slow as shit

    colors_ranges = {
        'blue': ([69, 120, 100], [179, 255, 255]),    
        'yellow': ([21, 110, 117], [45, 255, 255]),   
        'orange': ([0, 110, 125], [20, 255, 255]),
        'red': ([0, 100, 100], [10, 255, 255]),
        'green': ([36,100,50], [86,255,255]),
        'white': ([0, 0, 150], [255, 100, 255])
        }
        
    colors_lab = {
        "red": (185, 0, 0),
        "blue": (0, 0, 255),
        "green": (38, 106, 46), # bright (0, 155, 72)
        "yellow": (255, 213, 0),
        "orange": (255, 165, 8),
        "white": (255, 255, 255)
    }    
    
    # if colorName is not None:
    #     colors_lab[colorName] = (value['0'], value['1'], value['2'])
    
    
    if colors is not None:
        for key, value in colors.items():
            colors_lab[key] = [value[str(i)] for i in range(3)]
    

    # we create a image with a pixel for each lab converted color from the color dict (nigga)    
    lab_space = np.zeros((len(colors_lab), 1, 3), dtype="uint8")
    for count, (key, value) in enumerate(colors_lab.items()):
        lab_space[count] = value # value = rgb

    lab_space = cv2.cvtColor(lab_space, cv2.COLOR_RGB2LAB)

    # Color threshold to find the squares
    open_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    for color, (lower, upper) in colors_ranges.items():
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        color_mask = cv2.inRange(image, lower, upper)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, open_kernel, iterations=1)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, close_kernel, iterations=5)

        color_mask = cv2.merge([color_mask, color_mask, color_mask])
        mask = cv2.bitwise_or(mask, color_mask)

    gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    cnts = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnts = imutils.grab_contours(cnts)
    cnts = list(filter(lambda cnt: math.isclose(cv2.contourArea(cnt), reduce(lambda x,y:x*y,cv2.boundingRect(cnt)[2:]), rel_tol=0.2), cnts))
    # if area nigga is smoll boi then fuck off to oblivion
    # cnts = list(filter(lambda cnt: cv2.contourArea(cnt) > 100, cnts))
    
    print(len(cnts))
    
    cnts = sorted(cnts, key=lambda c: cv2.boundingRect(c)[1], reverse=False) # sort top to bottom
    cnts_matrix = [sorted(cnts[i*3:(i+1)*3], key=lambda c: cv2.boundingRect(c)[0], reverse=False) for i in range(3)] # left to right
    colors_matrix =  [ [ 0 for i in range(3) ] for j in range(3) ]

    
    maxmin = {
    "maxX" : 0,
    "minX" : np.inf,
    "maxY" : 0,
    "minY" : np.inf
    }
    
    
    
    # for c in cnts:
    #     cv2.drawContours(original, [c], -1, (0, 255, 0), 2)
    
    for y in range(len(cnts_matrix)):
        for x in range(len(cnts_matrix[0])):
            c = cnts_matrix[y][x]
    
            epsilon = 0.05*cv2.arcLength(c,True)
            c_original = cv2.approxPolyDP(c,epsilon,True)
    
            c_for_extract = [points[0] for points in c_original]
            c = c_for_extract 
            for key in list(maxmin.keys()):
                candidate = max(c, key=itemgetter(0 if key[-1] == 'X' else 1)) if key[:-1] == 'max' else min(c, key=itemgetter(0 if key[-1] == 'X' else 1)) 
                candidate = candidate[0 if key[-1] == 'X' else 1]
                if key[:-1] == 'max':
                    if candidate > maxmin[key]:
                        maxmin[key] = candidate
                elif key[:-1] == 'min':
                    if candidate < maxmin[key]:
                        maxmin[key] = candidate
    
            c = c_original
    
            mask = np.zeros(lab_image.shape[:2], dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            mask = cv2.erode(mask, None, iterations=2)
            mean = cv2.mean(lab_image, mask=mask)[:3]
    
            minimum = [10000000, None] # the second in the list will hold the count (index of color in lab_space)
            for count, row in enumerate(lab_space):
                d = dist.euclidean(row[0], mean) # row[0] is the color because they're in column inside lab_space
                if d < minimum[0]:
                    minimum = [d, count]
            text = list(colors_lab.keys())[minimum[1]]
            colors_matrix[y][x] = text
            #cv2.drawContours(original, [c], -1, (0, 255, 0), 2)
    
            xx,yy,w,h = cv2.boundingRect(c)
            cv2.rectangle(original,(xx,yy),(xx+w,yy+h),(0,255,0),2)
    
            ratio = 1
            M = cv2.moments(c)
            cX = int((M["m10"] / M["m00"]) * ratio)
            cY = int((M["m01"] / M["m00"]) * ratio)
            cv2.putText(original, text, (cX-60, cY), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    
    original = original[maxmin["minY"]-30:maxmin["maxY"]+30, maxmin["minX"]-30:maxmin["maxX"]+30]
    if __name__ == '__main__':
        cv2.imshow('final', original)
        cv2.waitKey()
    return {"image": original, "colors_matrix": colors_matrix}    

if __name__ == '__main__':
    detect(cv2.imread('o2.jpeg'))

# def get_color_name(self, hsv):
#         """ Get the name of the color based on the hue.
#         :returns: string
#         """
#         (h,s,v) = hsv
#         #print((h,s,v))
#         if h < 15 and v < 100:
#             return 'red'
#         if h <= 10 and v > 100:
#             return 'orange'
#         elif h <= 30 and s <= 100:
#             return 'white'
#         elif h <= 40:
#             return 'yellow'
#         elif h <= 85:
#             return 'green'
#         elif h <= 130:
#             return 'blue'
