import math
import pygame
import numpy as np
from itertools import product
import sys
import cv2
from PIL import Image
import numexpr as ne
from timeit import default_timer as timer

images = [cv2.imread("{}.jpg".format(name))[0:360, 60:420] for name in ['cat', 'virus', 'hood']]
class point:
    def __init__(self, coor):
        self.coor = np.array(coor)
        
    def convert(self, field, dist):
        coefficient = field / (dist + self.coor[2]) # z
        self.coor[0] = self.coor[0] * coefficient + 1400 / 2 # x , 400 is width
        self.coor[1] = -self.coor[1] * coefficient + 1000 / 2 # y, 400 is height
        return self
        
    def rotate(self, axis, angle): # angle in nigga deg not rad arg
        theta = np.radians(angle)
        rotationMat = {
        "x" : np.array(( (1, 0, 0),
                        (0, np.cos(theta), -np.sin(theta)),
                       (0, np.sin(theta),  np.cos(theta)) )),
    
        "y" : np.array(( (np.cos(theta), 0, np.sin(theta)),
                        (0, 1, 0),
                       (-np.sin(theta),  0, np.cos(theta)) )),
    
        "z"  : np.array(( (np.cos(theta), -np.sin(theta), 0),
                       (np.sin(theta),  np.cos(theta), 0), 
                       (0, 0, 1) ))
        }
        self.coor = self.coor.dot(rotationMat[axis])
        return self
        
    def showCoor(self, which):
        return self.coor[which]
        
#  same | top |  left  |
#   x   |  1r |   2r   |
#   y   |  2r |   0    |
#   z   |  1r |   0    |
 
def transform(dicti, pointlist, top_deciding_coor, left_deciding_coor, top_reverse, left_reverse, image):
     cool_list = []
    # our goal is to create a list of indexes to tell us how to order the points in each face
     subdivisions = 2
     original_with_index = [pointt + [i] for i, pointt in enumerate(dicti["original"])]
     n = int(len(dicti["original"]) / subdivisions)
     # this will output [ top[point, point] , bottom[point, point] ]
     list_order_top_bottom = [sorted(original_with_index, key = lambda x: x[top_deciding_coor], reverse=top_reverse)[i:i+n] for i in range(0, len(dicti["original"]), n)]
     # now we want to sort the top and bottom layers according to left/right 
     list_order_top_bottom_left_right = [sorted(sub, key = lambda x: x[left_deciding_coor], reverse=left_reverse) for sub in list_order_top_bottom]
     # now we want to combine back to one array with 4 points
     total = []
     for i in list_order_top_bottom_left_right:
         total += i
     # indexes
     order = [pointt[3] for pointt in total]
     # and now for the 1000000 IQ trick (only rick and morty fans will understand)
     
     pointlist_with_index = [pointt+[i] for i, pointt in enumerate(pointlist)] 
     # print(pointlist_with_index)
     # print()
     # print(order)
     # can't concatenate list to tuple in pointlist 
     
     # now we have pointlist with attached indexes, we just need to sort
     correct_pointlist = []
     for i in range(len(pointlist)):
         correct_index = order[i]
         # find in list with indexes the point that has that (let's try filter)
         #print(order[i])
         #correct_vertex = list(filter(lambda x: x[2] == order[i], pointlist_with_index))
         correct_vertex = [pointt[:-1] for pointt in pointlist_with_index if pointt[2] == order[i]]
         correct_pointlist.append(correct_vertex)
     # print(correct_pointlist)
     #print(colors[dicti["index"]])
     
     #####################################################################################################
     # now we have the correct pointlist
    
     height, width, channels = image.shape 
     # itertools.product([0, width],[0, height])
     # cartesian product
     
     ##################################################################################################### homography RANSAC
     # h, status = cv2.findHomography(np.array([[0, 0], [width, 0], [0, height], [width, height]]), 
     #     np.array(correct_pointlist))
     # image_affine_applied = cv2.warpPerspective(image, h, (1500,1500))
     
     ###################################################################################################### affine transformation
     # M = cv2.getAffineTransform(np.float32([[0, 0], [width, 0], [0, height]]),
     #     np.float32(correct_pointlist[:3]))
     # image_affine_applied = cv2.warpAffine(image, M, (1500, 1500))
     
     ######################################################################################################
     
     M = cv2.getPerspectiveTransform(np.float32([[0, 0], [width, 0], [0, height], [width, height]]), 
         np.float32(correct_pointlist))
     image_affine_applied = cv2.warpPerspective(image,M,(1400,1000))
     
     ######################################################################################################
     
     #cv2.imshow("image", image_affine_applied)
     #cv2.waitKey(1)    
     cool_list.append(image_affine_applied)
     return cool_list
 
 
def mainCube():
    global image
    colors = list(product([0, 255], repeat=3))[1:]
    colors.remove((255, 255, 255))
    pygame.init()
    DISPLAY = pygame.display.set_mode((1400, 1000))

    faces  = [(0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(0,4,5,1),(3,2,6,7)]
    clock = pygame.time.Clock()
    
    angle = 0

    prevAngleX = 0
    prevAngleY = 0
    prevPos = None
    angleX = 0
    angleY = 0
    pos = None
    start = False
    
    while True:
        
        
        if pygame.mouse.get_pressed()[0] == 1:
            start = True
            if prevPos:
                pos = pygame.mouse.get_pos()
                deltaX = pos[0] - prevPos[0]
                deltaY = pos[1] - prevPos[1]
            
                angleX = prevAngleX + deltaY/3
                angleY = prevAngleY + deltaX/3

                prevPos = pos
            else:
                prevPos = pygame.mouse.get_pos()
        else:
            if start == True:
                prevPos = None
        
        clock.tick(50)
        
        # vertices = [point(coor) for coor in list(product([1, -1], repeat=3))]
        
        vertices_no_object = [
            [-1,1,-1],
            [1,1,-1],
            [1,-1,-1],
            [-1,-1,-1],
            [-1,1,1],
            [1,1,1],
            [1,-1,1],
            [-1,-1,1]
        ]
        
        vertices = [point(vertex) for vertex in vertices_no_object]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        
        #clock.tick(50)
        DISPLAY.fill((0,10,0))

        transformed = []
        angleX = angleX % 360
        angleY = angleY % 360
        
        
        for vertex in vertices:
            transformed.append((  vertex.rotate("y", angleY).rotate("x", angleX).convert(500, 4) ))
            
        prevAngleX = angleX
        prevAngleY = angleY
        
            #calculate average z to know what to draw
        average_z_list = []
        index = 0
        for face in faces:
            
            # we want to find for each face which coordinate stays the same
            points_list = [vertices_no_object[index] for index in face]

            for coor in [0, 1, 2]:
                if all([pointt[coor] == points_list[0][coor] for pointt in points_list]):
                    coor_no_change = coor
            
            
            z = [transformed[face[i]].coor[2] for i in range(len(face))]    
            average_z = sum(z) / 4 # /4

            average_z_list.append({"index" : index, "avg" : average_z, "coor_no_change" : coor_no_change, "original": points_list})
            index = index + 1
        average_z_list.sort(key=lambda dicti: dicti['avg'], reverse=True)
            
            
        cool_list = []    
        for c, dicti in enumerate(average_z_list):
            face = faces[dicti["index"]]
            
            pointlist = [[transformed[face[0]].coor[0], transformed[face[0]].coor[1]], [transformed[face[2]].coor[0], transformed[face[2]].coor[1]], [transformed[face[1]].coor[0], transformed[face[1]].coor[1]], [transformed[face[3]].coor[0], transformed[face[3]].coor[1]]]
            
            
            pointlist[1], pointlist[2] = pointlist[2], pointlist[1]
            
            
            
            # if dicti["index"] == 0:
            #     print(colors[dicti["index"]])
            #     affine = cv2.getAffineTransform(np.array([[0, 0], [0, len(image)], [len(image), 0]], np.float32), 
            #         np.array(pointlist[:3], np.float32))
            #     image_affine_applied = cv2.warpAffine(image, affine, (1000,1000))
            #     cv2.imshow("image", image_affine_applied)
            #     cv2.waitKey(1)
            
            
            
            # order
            # np.array([[0, len(image[0])], [0, 0], [len(image), 0], [len(image[0]), len(image)]])
            
            
            #print(dicti["coor_no_change"])
            
            #  same | top |  left  |
            #   x   |  1r |   2r   |
            #   y   |  2r |   0    |
            #   z   |  1r |   0    |
            
            if c > 2:
                if dicti["coor_no_change"] == 0: #x
                    cool_list.extend(transform(dicti, pointlist, 1, 2, True, True, images[dicti["coor_no_change"]]))
                elif dicti["coor_no_change"] == 1: #y
                    cool_list.extend(transform(dicti, pointlist, 2, 0, True, False, images[dicti["coor_no_change"]]))
                else: #z
                    # front 
                    cool_list.extend(transform(dicti, pointlist, 1, 0, True, False, images[dicti["coor_no_change"]]))
                
        
        #print(len(cool_list))
        cool_list = cool_list
        #final = cv2.bitwise_or(cool_list[0], cool_list[1]) 
        #final = cv2.addWeighted(cool_list[0], 1, cool_list[1], 0.1, 0)
        
        
        
        ######################################### big chungus code ########################################################
        
        # cool_list_pil = [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) for img in cool_list]
        # front_mask = Image.fromarray(np.any(cool_list[0] != [0, 0, 0], axis=-1))
        # print(front_mask)
        # cool_list_pil[1].paste(cool_list_pil[0], mask=front_mask)
        # 
        # backToCV = np.array(cool_list_pil[1])
        # backToCV = cv2.cvtColor(backToCV, cv2.COLOR_RGB2BGR) 
        # 
        # cv2.imshow("final", backToCV)
        # cv2.waitKey(1)
        
        ###################################### big floppa code ##############################################################
        
        # print("nigga")
        # print(cool_list[1][0][0])
        def paste(background, front):
            arr = [0, 0, 0]
            notBlack = ne.evaluate("front != arr")
            background[notBlack] = front[notBlack]
            return background
        
        # cv2.imshow("final", paste(cool_list[0], cool_list[1]))
        # cv2.waitKey(1)
        
        final = cool_list[0]
        for i in range(1, len(cool_list)):
            final = paste(final, cool_list[i])
            
        final = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)    
        final_pygame = pygame.image.frombuffer(final.tostring(), final.shape[1::-1], 'RGB')    
            
        # cv2.imshow("final", final)
        # cv2.waitKey(1)
        
        DISPLAY.blit(final_pygame, (0, 0))


            
            # if dicti["index"] == 0:
            #     #print(colors[dicti["index"]])
            #     height, width, channels = image.shape 
            #     # itertools.product([0, width],[0, height])
            #     # cartesian product
            #     h, status = cv2.findHomography(np.array([[0, 0], [width, 0], [0, height], [width, height]]), 
            #         np.array(pointlist))
            #     image_affine_applied = cv2.warpPerspective(image, h, (1500,1500))
            #     cv2.imshow("image", image_affine_applied)
            #     cv2.waitKey(1)
            
            
            # pointlist = [(transformed[face[0]].coor[0], transformed[face[0]].coor[1]), (transformed[face[1]].coor[0], transformed[face[1]].coor[1]),
            #              (transformed[face[1]].coor[0], transformed[face[1]].coor[1]), (transformed[face[2]].coor[0], transformed[face[2]].coor[1]),
            #              (transformed[face[2]].coor[0], transformed[face[2]].coor[1]), (transformed[face[3]].coor[0], transformed[face[3]].coor[1]),
            #              (transformed[face[3]].coor[0], transformed[face[3]].coor[1]), (transformed[face[0]].coor[0], transformed[face[0]].coor[1])]
            # 
            # pointlist = [[[transformed[face[i]].coor[0], transformed[face[i]].coor[1]], [transformed[face[i+1]].coor[0], transformed[face[i+1]].coor[1]]] for i in range(3)]
            # pointlist.append( [[transformed[face[3]].coor[0], transformed[face[3]].coor[1]], [transformed[face[0]].coor[0], transformed[face[0]].coor[1]]] )
            #we need to flatten matrix
            # from [[],[]], [[],[]] to [], [], [], []
            #pointlist = [point for duo in pointlist for point in duo ]
            #pygame.draw.polygon(DISPLAY, colors[dicti["index"]], pointlist)
        pygame.display.flip()
            
if __name__ == "__main__":
    mainCube()
