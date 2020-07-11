import pygame
import sys
from pygame.locals import *
from itertools import starmap, product
import random
from collections import deque
import time
#from threedcube import point
import numpy as np
import concurrent.futures
from threading import Timer, Thread, Event
import requests
import json
import tkinter as tk
import os
import operator

stop = False    
counter = 0   

colors = {
"w":"white",
"g":"green",
"r":"red",
"b":"blue",
"o":"orange",
"y":"yellow"
}

keeperArrows = 0
isYellowOnTop = False

def main(code=None):
    global keeperArrows
    global isYellowOnTop
    
    # ok, so when we do left or right arrow, we need to rotate
    
    
    vertices = [
        [-1,1,-1],
        [1,1,-1],
        [1,-1,-1],
        [-1,-1,-1],
        [-1,1,1],
        [1,1,1],
        [1,-1,1],
        [-1,-1,1]
    ]
    
    verticesTopBottom = [[vertices.index(coor) for coor in list(filter(lambda x: x[1] == val, vertices))] for val in (-1, 1)]
    print(verticesTopBottom)
    
    # מכפלה קרטזית
    combos = list(product((-1, 1), ("x", "z")))
    
    print(combos)
    verticesRBOG = [[vertices.index(coor) for coor in list(filter(lambda x: x[0 if coorValCombo[1] is "x" else 2] == coorValCombo[0], vertices))] for coorValCombo in combos]
    
    print(verticesRBOG)
    
    verticesRBOG.insert(0, verticesTopBottom[1])
    verticesRBOG.insert(len(verticesRBOG), verticesTopBottom[0])
    
    faces = verticesRBOG
    
    print("tie")
    print(faces)
    
    #faces = [(4,5,6,7), (1,5,6,2), (3, 2, 6, 7), (4,0,3,7), (0,4,5,1), (0,1,2,3)][::-1]
    
    # the first face should be the one where  all y values are 1
    # the last one where all the y's are -1
    # the rest should be in order rbog (red to right)
    
    final_squares = []
    
    # my goal: for every face (4 vertices) create a matrix of 9 squares, the colors will be assigned to them
    
    # in all sides, there will always be one coordinate that stays the same, I want to identify it (and what it equals to)
    # for example in the front face z is the same but x and y change
    
            
    # now we know which coor stays the same
    # the rest will go from -1 to 1 (for the 2 other coors) in increments of 2/3 each time (2 = 1-(-1) the delta)
    
    for face in faces:
        faceNewPoints = []
        coorNoChange = None
        coorNoChangeValue = None
        points = [vertices[index] for index in face]
        #print(all(point[coor]==points[0][coor] for point in points for coor in [0, 1, 2]))
        for coor in [0, 1, 2]:
            if all(point[coor]==points[0][coor] for point in points):
                coorNoChange = coor
                coorNoChangeValue = points[0][coor]
        # we want to skip the iteration if the coor is the one that doesn't change
        # but that would be difficult so we'll remove duplicates later on
        for z in range(3):
            for y in range(3):
                for x in range(3):
                    point = [None, None, None]
                    for coor in [0, 1, 2]:
                        if coor is coorNoChange:
                            point[coor] = coorNoChangeValue
                        else:
                            point[coor] = -1 + (2/3)*y if coor is 1 else -1 + (2/3)*x if coor is 0 else -1 + (2/3)*z # if coor is 2
                            # I typed 1 instead of 0 which fucked up the code (3 new points after filter in the last 2 sides instead of 4)
                            
                    faceNewPoints.append(point)
        #faceNewPoints = list(set(faceNewPoints)) # this doesn't work with matrix :(
        newFaceNewPoints = []
        for elem in faceNewPoints:
            if elem not in newFaceNewPoints:
                newFaceNewPoints.append(elem)
        faceNewPoints = newFaceNewPoints
        #print(faceNewPoints)
        
        
        # now we want the 3 other points (the form the squares for the polygon draw function)
        #print(len(faceNewPoints))
        for point in faceNewPoints:
            square = [point, None, None, None]
            optionalCoors = [0, 1, 2]
            optionalCoors.remove(coorNoChange)
            #print(optionalCoors)
            for i in range(len(optionalCoors)):
                #print(point)
                new = square[0][:]
                new[optionalCoors[i]] = new[optionalCoors[i]] + 2/3
                square[i+1] = new
            square[3] = square[0][:]
            for optionalCoor in optionalCoors:
                square[3][optionalCoor] = square[3][optionalCoor] + 2/3
            
            # VERY IMPORTANT: it turns out that assigning square[0] to new creates an unwanted reference which causes problems in iteration
            final_squares.append(square)
            #print(square)
            print(" ")
        
    pygame.init()
    DISPLAY = pygame.display.set_mode((2000, 1000))
    clock = pygame.time.Clock()

    selection = {"front": True, "top": False, "bottom": False}

    matrix1 = [
    [0, 1, 0, 0],
    [1, 1, 1, 1],
    [0, 1, 0, 0]
    ]

    def randomCube():
        for y in range(len(matrix1)):
            for x in range(len(matrix1[y])):
                if matrix1[y][x] is not 0:
                    matrix1[y][x] = [[random.choice(list(colors.keys())) for j in range(3)] for i in range(3)]

    def startCubeSolved():
        counter = 0
        for y in range(len(matrix1)):
            for x in range(len(matrix1[y])):
                if matrix1[y][x] is not 0:
                    matrix1[y][x] = [[list(colors.keys())[counter] for j in range(3)] for i in range(3)]
                    counter = counter + 1

    matrix_color_indicator = [
        [0, 'w', 0, 0],
        ['b', 'o', 'g', 'r'],
        [0, 'y', 0, 0]
    ]
    
    #matrix_color_placeholder = [[ 0 for x in range(4)] for y in range(3)]

    #URL = "http://127.0.0.1:5000/useCode" # for now local host
    
    
    URL = "https://rubix-isaac.herokuapp.com/useCode" # now heroku
    
    # print(code)
    # #code = 'bioq'
    # data = requests.post(url=URL, json={'code':code}).json()["stringColor"]
    # print(data)
    # 
    # #data = list("wwwwwwwwwrrrrrrrrrgggggggggbbbbbbbbbyyyyyyyyyooooooooo")
    # data = np.array(list(data)).reshape((int(len(data)/9), 3, 3))
    # 
    # for y in range(len(matrix_color_indicator)):
    #     for x in range(len(matrix_color_indicator[y])):
    #         for matrixdata in data:
    #             if matrix_color_indicator[y][x] == matrixdata[1][1]:
    #                 matrix1[y][x] = matrixdata
    # 
            
    startCubeSolved()

    mat1 = [
    ["r", "g", "b"],
    ["w", "g", "o"],
    ["b", "w", "y"]
    ]



    offsetX = 50
    offsetY = 50
    height = 100
    width = 100

    def scramble(matrix):
        global keeperArrows
        if (random.random() < 0.5):
            matrix = switch(matrix, counter=random.random() > 0.5)
            if random.random() > 0.7:
                rightleftswitchscramble = 'right' if random.random() > 0.5 else 'left'
                matrix = switchFront(matrix, right=True if rightleftswitchscramble == 'right' else False)
                keeperArrows = keeperArrows + 1 if rightleftswitchscramble == "right" else keeperArrows - 1
        else:
            matrix = rotateTopBottom(matrix, top=random.random() > 0.5, counter=random.random() > 0.5)
        drawCube(matrix)
        return matrix
        
    # i want the delay here to not stop the entire code

    def rotateTopBottom(matrix, top=True, counter=True):
        prevRowList = []
        matrix[0 if top else 2][1] = rotate90deg(matrix[0 if top else 2][1], not counter)
        if top == False:
            for i in range(4):
                try:
                    prevRowList.append(matrix[1][i-1 if not counter else i+1][0 if top else 2]) # order according to counter/cw
                except IndexError:  # if we are clockwise (not counter) then i+1 will return index error RIP
                    prevRowList.append(matrix[1][0][0 if top else 2])
        else:
            for i in range(4):
                try:
                    prevRowList.append(matrix[1][i-1 if counter else i+1][0 if top else 2]) # order according to counter/cw
                except IndexError:  # if we are clockwise (not counter) then i+1 will return index error RIP
                    prevRowList.append(matrix[1][0][0 if top else 2])
        
        for i in range(4):
            matrix[1][i][0 if top else 2] =  prevRowList[i]
        return matrix

    def drawMatrix(matrix, yy, xx):
        for y in range(len(matrix)):
            for x in range(len(matrix[y])):
                pygame.draw.rect(DISPLAY, pygame.Color(colors[matrix[y][x]]), (offsetX+x*width+xx*width*3, offsetY+y*height+yy*height*3, height, width), 0)
                pygame.draw.rect(DISPLAY, pygame.Color("black"), (offsetX+x*width+xx*width*3, offsetY+y*height+yy*height*3, height, width), 2)

    buttonRotateAnti = pygame.draw.rect(DISPLAY, pygame.Color("red") ,(0, 0, 50, 50))
    buttonRotate = pygame.draw.rect(DISPLAY, pygame.Color("orange") ,(50, 0, 50, 50))
    buttonFrontRight = pygame.draw.rect(DISPLAY, pygame.Color("blue") ,(0, 50, 50, 50))
    buttonFrontLeft = pygame.draw.rect(DISPLAY, pygame.Color("green") ,(50, 50, 50, 50))

    buttonScramble = pygame.draw.rect(DISPLAY, pygame.Color("purple") ,(0, 150, 50, 50))
    
    solveWhiteCrossButton = pygame.draw.rect(DISPLAY, pygame.Color("purple"), (1200, 0, 50, 50))
    solveWhiteCornersButton = pygame.draw.rect(DISPLAY, pygame.Color("orange"), (1200, 50, 50, 50))
    yellowOnTopButton = pygame.draw.rect(DISPLAY, pygame.Color("yellow"), (1200, 100, 50, 50))

    selection_buttons = { # this will store the args to pass to draw buttons
        "front": (0, 100, 50, 50),
        "top": (50, 100, 50, 50),
        "bottom": (100, 100, 50, 50),
    }

    selection_text = {
        "front": (5, 88),
        "top": (55, 88),
        "bottom": (105, 88),
    }


    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)


    f = pygame.font.Font(resource_path("nigga.ttf"),64) # 64
    DISPLAY.blit(f.render("↺", True, (255, 255, 255)) , (5, -12))
    DISPLAY.blit(f.render("↻", True, (255, 255, 255)) , (55, -12))
    DISPLAY.blit(f.render("→", True, (255, 255, 255)) , (5, 38))
    DISPLAY.blit(f.render("←", True, (255, 255, 255)) , (55, 38))

    #counterclockwise = right, clockwise = left

    def drawCube(matrix):
        for y in range(len(matrix)):
            for x in range(len(matrix[y])):
                if matrix[y][x] is not 0:
                    drawMatrix(matrix[y][x], y, x)

    def transposeMatrix(matrix):
        return [[matrix[y][x] for y in range(len(matrix))] for x in range(len(matrix[0]))]

    def rotate90deg(matrix, clockwise):
        return [array[::-1] for array in transposeMatrix(matrix)] if clockwise else transposeMatrix(matrix)[::-1]

    def getNeighbors(matrix, x, y, getIndexes=False):
        indexes = starmap((lambda a, b: [x+a, y+b]), product((-1, 0, 1), (-1, 0, 1))) # this will return list of x, y coors for 2d mat
        indexes = filter(lambda index:  (0 <= index[0] < len(matrix) and (0 <= index[1] < len(matrix[index[0]])) ), list(indexes)) # filter the shit by checking if index smaller then len
        return [matrix[index[0]][index[1]] for index in indexes] if not getIndexes else indexes

    def switch(matrix, counter=True): # currently counter clockwise
        matrix[1][1] = rotate90deg(matrix[1][1], clockwise=not counter)
        def transIndex():
            matrix[neighIndexes[i][0]][neighIndexes[i][1]] = transposeMatrix(matrix[neighIndexes[i][0]][neighIndexes[i][1]])
        order = list(product(("reg", "trans"), (0, 2))) #reg/trans, 0/2
        order.sort(key=lambda x: x[1], reverse=True) # sort reg trans in order (counterclockwise from top)
        sides = list(filter(lambda side: side is not 0 and side is not matrix[1][1], getNeighbors(matrix, 1, 1)))
        neighIndexes = list(getNeighbors(matrix, 1, 1, getIndexes=True))
        neighIndexes = list(filter(lambda ix: matrix[ix[0]][ix[1]] is not 0 and matrix[ix[0]][ix[1]] is not matrix[1][1], getNeighbors(matrix, 1, 1, getIndexes=True)))
        sides[-1], sides[-2] = sides[-2], sides[-1] # sides in counterclockwise order from top
        neighIndexes[-1], neighIndexes[-2] = neighIndexes[-2], neighIndexes[-1]

        if counter==False:
            order[1], order[-1] = order[-1], order[1]
            sides[1], sides[-1] = sides[-1], sides[1]
            neighIndexes[1], neighIndexes[-1] = neighIndexes[-1], neighIndexes[1]
        prevRowList = []
        for i in range(len(neighIndexes)):
            prevRow = None
            if order[i-1][0] is "trans":
                row = transposeMatrix(matrix[neighIndexes[i-1][0]][neighIndexes[i-1][1]])[order[i-1][1]]
                if counter is True:
                    prevRowList.append(row)
                else:
                    prevRowList.append(row[::-1])
            else: #elif order[i-1][0] is "reg"
                prevRow = matrix[neighIndexes[i-1][0]][neighIndexes[i-1][1]][order[i-1][1]]
                if counter == True:
                    prevRow = prevRow[::-1] #if currently trans we need to inverse nigga (hoes mad warning)
                prevRowList.append(prevRow)
        for i in range(len(prevRowList)):
            if order[i-1][0] is "trans":
                matrix[neighIndexes[i][0]][neighIndexes[i][1]][order[i][1]] = prevRowList[i]
            else:
                transIndex()
                matrix[neighIndexes[i][0]][neighIndexes[i][1]][order[i][1]] = prevRowList[i]
                transIndex() # return to usual
        return matrix

    def switchFront(matrix, right=True):
        matrix[0][1] = rotate90deg(matrix[0][1], clockwise=not right) # if we move right we want anticlockwise in the top
        matrix[2][1] = rotate90deg(matrix[2][1], clockwise=right) # and the opposite in the bottom
        bar = deque(matrix[1])
        bar.rotate(1 if right else -1) # displace first & last elements
        matrix[1] = list(bar) # re-insert the nigga to the ghetto
        return matrix

    def yellowOnTop():
        pass
        
        
    def solveWhiteCross(matrix):
        global keeperArrows
        matrix = matrix[:]
        # the first in sublist in neighbors is in the yellow
        neighbors = [
            [ matrix[2][1][0][1] , matrix[1][1][2][1] ],
            [ matrix[2][1][1][2] , matrix[1][2][2][1] ],
            [ matrix[2][1][2][1] , matrix[1][3][2][1] ],
            [ matrix[2][1][1][0] , matrix[1][0][2][1] ]
        ]
        
        neighborsWithIndexes = [
            [[2, 1, 0, 1],[1, 1, 2, 1]],
            [[2, 1, 1, 2],[1, 2, 2, 1]],
            [[2, 1, 2, 1],[1, 3, 2, 1]],
            [[2, 1, 1, 0],[1, 0, 2, 1]]
        ]
        
        neighIndexesMiddleRow = [1, 2, 3, 0]
        
        whitiesGood = [x[1] for x in neighbors if x[0] == 'w']
        
        if len(whitiesGood) > 0:
            whitiesGoodIndex = [neighborsWithIndexes[i][1] for i in range(len(neighborsWithIndexes)) if neighbors[i][0] == 'w'][0]
            # we need to rotate bottom until the neighbor matches with side center
            # we rotate and the new indexes is from neighbors
            # we check if current index and the center of its side match
            # if yes save to variable representing color center and rotate till it's in the front
            # and after that rotate twice
            
            # just to clairfy when checking matching
            # we check neighbor (the new white pos) and the corresponding neighbor but tile above ([1][1 or 2 or 3 or 0][1 instead of 2][1])
            
            # if not already in solved pos
            
            if not matrix[1][whitiesGoodIndex[1]][2][1] == matrix[1][whitiesGoodIndex[1]][1][1]:
                indexInRow = whitiesGoodIndex[1] # (1, 2, 3, 0)
                print("indexInRow")
                print(indexInRow)
                while True:
                    print("turn")
                    indexInRow = indexInRow + 1
                    if indexInRow == 4:
                        indexInRow = 0
                    matrix = rotateTopBottom(matrix, top=False, counter=False)
                    if matrix[1][indexInRow][1][1] == matrix[1][indexInRow][2][1]:
                        colorKeeper = matrix[1][indexInRow][1][1]
                        while colorKeeper != matrix[1][1][1][1]:
                            matrix = switchFront(matrix, right=True)
                            keeperArrows = keeperArrows + 1
                        print("ok now good")
                        
                        break
                matrix = switch(matrix, counter=False)
                matrix = switch(matrix, counter=False)
            else:
                print("already solved white just need to rotate")
                indexInRow = whitiesGoodIndex[1]
                while True:
                    if matrix[1][indexInRow][2][1] == matrix[1][1][1][1]:
                        break
                    matrix = switchFront(matrix, right=True)
                    keeperArrows = keeperArrows + 1
                    indexInRow = indexInRow + 1
                    if indexInRow == 4:
                        indexInRow = 0
                matrix = switch(matrix, counter=False)
                matrix = switch(matrix, counter=False)
                
        else:
            whitiesThirdLayerGood = [x[0] for x in neighbors if x[1] == 'w'] # replaced zero and 1 in case white is not in the bottom but the third layer
            print(whitiesThirdLayerGood)
            if len(whitiesThirdLayerGood) != 0:
                whitiesThirdLayerGood = whitiesThirdLayerGood[0]
                print("we want to do the white third layer thingy")
                
                #######################################################
                whitiesThirdLayerGoodIndex = [neighborsWithIndexes[i][0] for i in range(len(neighborsWithIndexes)) if neighbors[i][1] == 'w'][0] # corresponding color to white lololololololololol el gringo
                actualWhitiesThirdLayerGoodIndex = [neighborsWithIndexes[i][1] for i in range(len(neighborsWithIndexes)) if neighbors[i][1] == 'w'][0] # actually white
                print(whitiesThirdLayerGoodIndex)
                
                # we need corresponding
                
                
                
                if not matrix[2][1][whitiesThirdLayerGoodIndex[2]][whitiesThirdLayerGoodIndex[3]] == matrix[1][actualWhitiesThirdLayerGoodIndex[1]][1][1]:
                    print("special case not already in solved pos need to match")
                
                    ##################################################################
                    
                    
                    # basically rotate bottom till matches
                    
                    indexBottom1 = whitiesThirdLayerGoodIndex[2]
                    indexBottom2 = whitiesThirdLayerGoodIndex[3]
                    indexesInBottom1 = [0, 1, 2, 1]
                    indexesInBottom2 = [1, 2, 1, 0]
                    
                    indexesInBottom = [
                        [0, 1],
                        [1, 2],
                        [2, 1],
                        [1, 0]
                    ]
                    
                    
                    
                    i = 0
                    while True:
                        print("rx")
                        print(matrix[2][1][indexBottom1][indexBottom2])
                        correctColor = matrix[2][1][indexBottom1][indexBottom2]
                        print("rx")
                        if matrix[1][(actualWhitiesThirdLayerGoodIndex[1]+i)%4][1][1] == matrix[2][1][indexBottom1][indexBottom2]:
                            break
                        matrix = rotateTopBottom(matrix, top=False, counter=False)
                        indexBottom1 = indexesInBottom1[(indexesInBottom1.index(indexBottom1)+1)%4]
                        indexBottom2 = indexesInBottom2[(indexesInBottom2.index(indexBottom2)+1)%4]
                        i = i + 1
                    
                    #ok now all we need to do is rotate till the right one is in the front
                    
                    
                    print("colololololol")
                    print(correctColor)
                    print("colololololol")
                    
                    while True:
                        if matrix[1][1][1][1] == correctColor:
                            break
                        matrix = switchFront(matrix, right=True)
                        keeperArrows = keeperArrows + 1
                        # maybe left is faster, check 
                    
                    
                    ##################################################################
                else:
                    print("special already solved just need to rotate potentially")
                    indexBottom1 = whitiesThirdLayerGoodIndex[2]
                    indexBottom2 = whitiesThirdLayerGoodIndex[3]
                    while True:
                        if matrix[1][1][1][1] == matrix[2][1][indexBottom1][indexBottom2]:
                            break
                        matrix = switchFront(matrix, right=True)
                        keeperArrows = keeperArrows + 1
                        
                        # now we have to change both indexes accordingly to list of potential ones
        
                        indexesInBottom1 = [0, 1, 2, 1]
                        indexesInBottom2 = [1, 2, 1, 0]
                        
                        # find index of indexBottom1 and indexBottom2 in indexesInBottom1 or 2 accordingly and select next one
                        indexBottom1 = indexesInBottom1[(indexesInBottom1.index(indexBottom1)+1)%4]
                        indexBottom2 = indexesInBottom2[(indexesInBottom2.index(indexBottom2)+1)%4]
                    
                    # after the loop
                    
                    
                    # now the algo
                    # matrix = switch(matrix, counter=False)
                    # matrix = rotateTopBottom(matrix, top=True, counter=True)
                    # matrix = switchFront(matrix, right=False) # to bring over the one from the right we need to switchFront left
                    # matrix = switch(matrix, counter=False)
                    # matrix = switchFront(matrix, right=True)
                    # matrix = rotateTopBottom(matrix, top=True, counter=False)
                    # 

            else:
                print("no whites in bottom")
                #find the neighboring edge pieces
                
                edgesCandidate = [[matrix[1][i-1][1][2],matrix[1][i][1][0]] for i in range(4)]
                
                print(edgesCandidate)
                edgesWhite = list(filter(lambda x: "w" in x, edgesCandidate))
                
                
                print(edgesWhite)
                
                #ok, now we have to shift front until it's in the middle
                # if index of the white is 0 than look for left in middle
                # if index of white is 2 then right
                # if it's first in neighbor subarray than it's 2 else 0
                
                # [2, 0]
                leftOrRight = "left" if edgesWhite[0].index("w") is 1 else "right" # if it's zero
                
                print(leftOrRight)
                
                if not matrix[1][1][1][0 if leftOrRight == 'left' else 2] == "w":
                    while True:
                        matrix = switchFront(matrix, right=True)
                        keeperArrows = keeperArrows + 1
                        if matrix[1][1][1][0 if leftOrRight == 'left' else 2] == "w":
                            break
                if leftOrRight == 'left':
                    matrix = switchFront(matrix, right=True)
                    matrix = switch(matrix, counter=False)
                    matrix = rotateTopBottom(matrix, top=False, counter=False)
                    matrix = switch(matrix, counter=True)
                    matrix = switchFront(matrix, right=False)
                    print(matrix)
                    print("left nigga")
                elif leftOrRight == 'right':
                    matrix = switchFront(matrix, right=False)
                    matrix = switch(matrix, counter=True)
                    matrix = rotateTopBottom(matrix, top=False, counter=True)
                    matrix = switch(matrix, counter=False)
                    matrix = switchFront(matrix, right=True)
                    print(matrix)
                    print("right nigga")
        
        return matrix

    drawCube(matrix1)
    
    def yellowOnTop(matrix):
        global isYellowOnTop
        isYellowOnTop = True
        
        # replace right and left
        matrix[1][0], matrix[1][2] = matrix[1][2], matrix[1][0]
        # invert them ([::-1] and rows)
        matrix[1][0] = matrix[1][0][::-1]
        matrix[1][0] = [row[::-1] for row in matrix[1][0]]
        matrix[1][2] = matrix[1][2][::-1]
        matrix[1][2] = [row[::-1] for row in matrix[1][2]]    
        # rotate front clockwise twice
        matrix[1][1] = rotate90deg(rotate90deg(matrix[1][1], clockwise=True), clockwise=True)
        # rotate behind counterclockwise twice
        matrix[1][3] = rotate90deg(rotate90deg(matrix[1][3], clockwise=False), clockwise=False)
        
        # now replace top and bottom
        matrix[0][1], matrix[2][1] = matrix[2][1], matrix[0][1]
        
        matrix[0][1] = matrix[0][1][::-1]
        matrix[0][1] = [row[::-1] for row in matrix[0][1]]
        matrix[2][1] = [row[::-1] for row in matrix[2][1]]
        matrix[2][1] = matrix[2][1][::-1]
        
        return matrix
    
    
    def solveWhiteCorners(matrix):
        

        top_corners = [
            [[0, 1, 2, 0], [1, 1, 0, 0], [1, 0, 0, 2]],
            [[0, 1, 2, 2], [1, 1, 0, 2], [1, 2, 0, 0]],
            [[0, 1, 0, 2], [1, 2, 0, 2], [1, 3, 0, 0]],
            [[0, 1, 0, 0], [1, 0, 0, 0], [1, 3, 0, 2]]
        ]
        
        
        #matrix = yellowOnTop(matrix)
        
        
        
        # bottom corners
        bottom_corners = [
            [[2, 1, 0, 0], [1, 1, 2, 0], [1, 0, 2, 2]], # good
            [[2, 1, 0, 2], [1, 1, 2, 2], [1, 2, 2, 0]], # good
            [[2, 1, 2, 2], [1, 2, 2, 2], [1, 3, 2, 0]], # good
            [[2, 1, 2, 0], [1, 0, 2, 0], [1, 3, 2, 2]] # good
        ]
    
    
        # coco = ['r', 'b', 'o', 'w']
        # for count, corner in enumerate(corners):
        #     for square in corner:
        #         matrix[square[0]][square[1]][square[2]][square[3]] = coco[count]
    
        corners_white = [corner for corner in top_corners if len(list(filter(lambda point: matrix[point[0]][point[1]][point[2]][point[3]] == 'w', corner)))]
    
        # now we want the other colors in the edge that are not white
        
        cornerObjects = []
        for i in range(len(top_corners)):
            cornerObjects.append({
                "isWhite": len(list(filter(lambda point: matrix[point[0]][point[1]][point[2]][point[3]] == 'w', top_corners[i]))),
                "sidesIndexes": sorted([point[1] for point in top_corners[i][1:]]), # the first one is left and the second right
                "colors": list(filter(lambda x: x != 'w', [matrix[point[0]][point[1]][point[2]][point[3]] for point in top_corners[i]]))
            })
        
        counterRotateTopBottom = 0
        
        print(cornerObjects)
        
        for i in range(len(top_corners)):
            if cornerObjects[i]["isWhite"] == 1:
                sides = cornerObjects[i]["sidesIndexes"]
                colors = cornerObjects[i]["colors"]
                while True:
                    print("counter"+str(counterRotateTopBottom))
                    if (matrix[1][sides[0]][1][1] == colors[0] or matrix[1][sides[0]][1][1] == colors[1]) and (matrix[1][sides[1]][1][1] == colors[0] or matrix[1][sides[1]][1][1] == colors[1]):
                            break
                    else:
                        # rotate top
                        matrix = rotateTopBottom(matrix, counter=True, top=True)
                        counterRotateTopBottom = counterRotateTopBottom + 1
                        # everytime we rotate TopBottom we need to change sides
        
        
                        sides = cornerObjects[(i+counterRotateTopBottom)%4]["sidesIndexes"]
                        # this was 3 instead of 4 which caused a huge problem
                        
                        
                #after the loop we want to switchFront until the color is in the front so the corner is in the right
                
                print("sides")
                print(sides)
                print("sides")
                print("colors")
                print(colors)
                print("colors")
                
                if sides == [0, 3]:
                    sides = sides[::-1]
                
                colors = [matrix[1][sides[i]][1][1] for i in range(len(sides))]
                
                print("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
                
                print("sides")
                print(sides)
                print("sides")
                print("colors")
                print(colors)
                print("colors")
                
                global keeperArrows
                while True:
                    if matrix[1][1][1][1] == colors[0]:
                        break
                    # the correct will be in the right
                    print("I had to... Is there a problem???")
                    matrix = switchFront(matrix)
                    keeperArrows = keeperArrows - 1
                    
                    
                # print("didi")
                # print(isCornerSolved(matrix, bottom_corners[1]))
                while True:
                    if isCornerSolved(matrix, bottom_corners[1]) == True:
                        break
                    # if the corresponding corner in the bottom is not solved we want to repeat the algo until it is
                    # the algo is the sexy move
                    # 1. switchFront to left 
                    # 2. rotate clockwise (switch)
                    # 3. rotate top clockwise
                    # 4. rotate counterclockwise (switch)
                    # 5. rotate top counterclockwise
                    # 6. switchFront to right (reset)
                    matrix = switchFront(matrix, right=False)
                    keeperArrows = keeperArrows + 1
                    matrix = switch(matrix, counter=False)
                    matrix = rotateTopBottom(matrix, top=True, counter=False)
                    matrix = switch(matrix, counter=True)
                    matrix = rotateTopBottom(matrix, top=True, counter=True)
                    matrix = switchFront(matrix, right=True)
                    keeperArrows = keeperArrows - 1
                    
                break
                    
        print(cornerObjects)
    
        return matrix
    


    def isCornerSolved(matrix, corner):
        isSolved = True
        for i in range(3):
            if matrix[corner[i][0]][corner[i][1]][1][1] != matrix[corner[i][0]][corner[i][1]][corner[i][2]][corner[i][3]]:
                isSolved = False
        return isSolved


    def buttonsFunc():
        global buttons
        buttons = [pygame.draw.rect(DISPLAY, pygame.Color("white") if selection[key] is False else pygame.Color("red") , value) for key, value in selection_buttons.items()]
        for key, value in selection_text.items():
            DISPLAY.blit(f.render(key[0], True, (0, 0, 0)) , value)
    buttonsFunc()
    
    
            
    colorsCube = list(product([0, 255], repeat=3))[1:]
    colorsCube.remove((255, 255, 255))

    faces  = [(0,1,2,3),(1,5,6,2),(5,4,7,6),(4,0,3,7),(0,4,5,1),(3,2,6,7)]
    faces = [(4,5,7,6), (1,5,6,2), (3, 2, 6, 7), (4,0,3,7), (0,4,5,1), (0,1,2,3)][::-1]

    
    angle = 0
    
    side = [
    ["r", "g", "b"],
    ["w", "g", "o"],
    ["b", "w", "y"]
    ]
    
    class point:
        def __init__(self, coor):
            self.coor = np.array(coor)
            
        def convert(self, field, dist):
            coefficient = field / (dist + self.coor[2]) # z
            self.coor[0] = self.coor[0] * coefficient + 2000 / 2 # x , 400 is width
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


    angle = 0

    prevAngleX = 0
    prevAngleY = 0
    prevPos = None
    angleX = 0
    angleY = 0
    pos = None
    start = False

    while True:
        # vertices = [point(coor) for coor in list(product([1, -1], repeat=3))]

        squaresPoint = [[point(pointX) for pointX in square] for square in final_squares]
        
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
            
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(50)
        DISPLAY.fill((0,0,0), (1300, 0, 2000, 1000))

        transformed = []
        angleX = angleX % 360
        angleY = angleY % 360
        for count, square in enumerate(squaresPoint):
            transformed.append([])
            for pointClass in square:
                transformed[count].append(pointClass.rotate("y", angleY).rotate("x", angleX).convert(500, 4))
                
                
        # for some reason the x angle creates problem
        
        # when 0 and 90        
           
        
        # now we need to get average z of all the squares and sort them in draw order
        # but instead of doing this invidually for each little square we can do it on the large ones
        # or not :) fuck computational intensity suck my dick
        average_z_list = []
        index = 0
        for square in transformed:
            z = [square[i].coor[2] for i in range(len(square))]
            average_z = sum(z) / 4
            average_z_list.append({"index": index, "avg": average_z})
            index = index + 1
        
        average_z_list.sort(key = lambda dicti: dicti["avg"], reverse=True)
        print
        
    
        for dicti in average_z_list:
            square = transformed[dicti["index"]]
            pointlist = [pointClass.coor[:-1] for pointClass in square]
            pointlist[3], pointlist[2] = pointlist[2], pointlist[3] 
            # we want to add x and y to point list to move the entire cube
            for i in range(len(pointlist)):
                pointlist[i][0] = pointlist[i][0] + 600
                pointlist[i][1] = pointlist[i][1] + 0
                
            indexNow = dicti["index"]
            sideNumber = indexNow//9 # now we have a number, but we want x, y in matrix1 to know which we are talking about
            
            array = [[0, 1], [1, 0], [1, 1], [1, 2], [1, 3], [2, 1]] # only with color
            
            y_index = array[sideNumber][0]
            x_index = array[sideNumber][1]
            
            side = matrix1[y_index][x_index]
            
            # now we have to rotate accordingly!!!!!!!!!!!!
            

            
            colorForArrowFix = ['g', 'r', 'b', 'o']
            
            g = colorForArrowFix[keeperArrows%4]
            r = colorForArrowFix[(keeperArrows+1)%4]
            b = colorForArrowFix[(keeperArrows+2)%4]
            o = colorForArrowFix[(keeperArrows+3)%4]
            
            if side[1][1] == g:
                side = rotate90deg(side, clockwise=True)
                side = rotate90deg(side, clockwise=True)
            elif side[1][1] == r:
                side = rotate90deg(side, clockwise=True)
            elif side[1][1] == b:
                side = side[::-1]
            elif side[1][1] == o:
                side = side[::-1]
                side = rotate90deg(side, clockwise=False)
                #side = [row[::-1] for row in side]
            elif side[1][1] == "y":
                side = side[::-1]
                side = rotate90deg(side, clockwise=True)
            elif side[1][1] == "w":
                side = rotate90deg(side, clockwise=True)
            # 
            # couldn't idenify any pattern here... just trial and error my friends....
            
            # 
            # when arrow right add 1, when arrow left sub 1
            if keeperArrows % 2 != 0: # notice the % 2, that's cause we goin to reset the move after 2
            # let's say we arrow left twice, that's -2 in keeperArrows
            # we don't want to rotate90deg, we wanna treat as if it was 0
            # -2%2=0
            #['y', 'b', 'g', 'w']
                r = colorForArrowFix[(-keeperArrows+1)%4]
                o = colorForArrowFix[(-keeperArrows+3)%4]
                if side[1][1] not in ['y', 'w']:
                    # side = side[::-1]
                    # side = rotate90deg(side, clockwise=True)
                    # side = rotate90deg(side, clockwise=True)
                    side = [row[::-1] for row in side]
                if side[1][1] in [r, o]:
                    side = [row[::-1] for row in side]
                    side = side[::-1]
    
    
    
    
            # we want to test:
            # if yellow on edge:
            # top and bottom need to be [::-1]d
            # and right and left in RBOG row should be row[::-1]d
    
    
            
            
            RBOGrawColors = ['g', 'r', 'b', 'o'] # 0,1,2,3
            
            for i in range(keeperArrows%4):
                RBOGrawColors.insert(0, RBOGrawColors.pop(len(RBOGrawColors)-1) )
                
            # I have no idea why the -1 is required :((()))
            
            rightRBOG = RBOGrawColors[2]
            leftRBOG = RBOGrawColors[0]
            
            
            if isYellowOnTop:
                if side[1][1] == rightRBOG or side[1][1] == leftRBOG:
                    side = [row[::-1] for row in side]
                    
                if side[1][1] == 'w': # w = bottom
                    pass
                    #side = rotate90deg(rotate90deg(side, clockwise=True), clockwise=True)
                    side = [row[::-1] for row in side]
                    #side = side[::-1]
                if side[1][1] == 'y': # y = top
                    pass
                    #side = rotate90deg(rotate90deg(side, clockwise=True), clockwise=True)
                    side = [row[::-1] for row in side]
                    #side = side[::-1]
                    
            # right = anti-clockwise
            # left = clockwise
            
                                                # for example 4
            # if keeperArrows == 2 or (keeperArrows > 2 and keeperArrows % 2 == 0):
            #     side = rotate90deg(side, clockwise=True)
            #     side = rotate90deg(side, clockwise=True)
            # 
            # reason?
            
            
            #we still need to invert rows
            #but only in front and behind
            
            
            prevAngleX = angleX
            prevAngleY = angleY
            
            
            
            
            
            
            pygame.draw.polygon(DISPLAY, pygame.Color(colors[side[dicti["index"]%9%3][dicti["index"]%9//3]]), pointlist)
            
            for i in range(len(pointlist)):
                pygame.draw.line(DISPLAY, pygame.Color("black"), pointlist[i-1], pointlist[i])          
            
        pygame.display.flip()        
            
            
         
            
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for count, button in enumerate(buttons):
                    if button.collidepoint(mouse_pos):
                        which = list(selection_buttons.keys())[count]
                        print(which)
                        for key, value in selection.items():
                            selection[key] = True
                            if not key is which:
                                selection[key] = False
                        buttonsFunc()
            
                if buttonScramble.collidepoint(mouse_pos):
                    global counter
                    counter = 0
                    # t = threading.Thread(target=scramble)
                    # t.start()
                    # with concurrent.futures.ThreadPoolExecutor() as executor:
                    #     future = executor.submit(scramble, matrix1)
                    #     return_value = future.result()
                    #     matrix1 = return_value
                    
                    class perpetualTimer():
                        def __init__(self,t,hFunction, arg, counter):
                          self.counter = counter
                          self.arg = arg   
                          self.t=t
                          self.hFunction = hFunction
                          self.thread = Timer(self.t,self.handle_function)

                        def handle_function(self):
                            if counter is not 10:
                              self.hFunction(self.arg)
                              self.thread = Timer(self.t,self.handle_function)
                              self.thread.start()

                        def start(self):
                          self.thread.start()

                        def cancel(self):
                          self.thread.cancel()
                    
                    def inner(matrix):
                        global stop
                        global counter
                        counter = counter + 1
                        matrix = scramble(matrix)
                        pygame.display.update()
                        #print(counter)
                    
                            
                    #global counter    
                    t = perpetualTimer(0.2, inner, matrix1, counter)
                    t.start()
                    
                if solveWhiteCrossButton.collidepoint(mouse_pos):
                    matrix1 = solveWhiteCross(matrix1[0:])
                    drawCube(matrix1)
                        
                if solveWhiteCornersButton.collidepoint(mouse_pos):
                    #
                    matrix1 = solveWhiteCorners(matrix1[0:])
                    drawCube(matrix1)
                    
                if yellowOnTopButton.collidepoint(mouse_pos):
                    matrix1 = yellowOnTop(matrix1)
                    drawCube(matrix1)  
            
                if buttonRotateAnti.collidepoint(mouse_pos):
                    if selection["front"] is True:
                        matrix1 = switch(matrix1, counter=True)
                    else:
                        matrix1 = rotateTopBottom(matrix1, top=selection["top"], counter=True)
                    drawCube(matrix1)
            
                if buttonRotate.collidepoint(mouse_pos):
                    if selection["front"] is True:
                        matrix1 = switch(matrix1, counter=False)
                    else:
                        matrix1 = rotateTopBottom(matrix1, top=selection["top"], counter=False)
                    drawCube(matrix1)
            
                if buttonFrontRight.collidepoint(mouse_pos):
                    matrix1 = switchFront(matrix1)
                    drawCube(matrix1)
                    keeperArrows = keeperArrows + 1
                if buttonFrontLeft.collidepoint(mouse_pos):
                    matrix1 = switchFront(matrix1, right=False)
                    drawCube(matrix1)
                    keeperArrows = keeperArrows - 1
            
        
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

# master = tk.Tk()
# tk.Label(master, text="Enter your code  ").grid(row=0)
# code = tk.Entry(master)
# code.grid(row=0, column=1)
# tk.Button(master, 
#           text='Done', 
#           command=master.quit).grid(row=3, 
#                                     column=0, 
#                                     sticky=tk.W, 
#                                     pady=4)
# master.mainloop()
# main(code=code.get())
main()
