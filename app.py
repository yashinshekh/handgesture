import cv2
import numpy as np
import math
import os
import pygame
from mutagen.id3 import ID3
from tkinter import *
import time

root = Tk()
root.minsize(300,300)


listofsongs = []
realnames = []

v = StringVar()
songlabel = Label(root,textvariable=v,width=35)

index = 0

def directorychooser():

    # directory = askdirectory()
    # os.chdir(directory)

    for files in os.listdir(os.getcwd()):
        if files.endswith(".mp3"):

            realdir = os.path.realpath(files)
            audio = ID3(realdir)
            print audio
            realnames.append(audio['TSSE'].text[0])


            listofsongs.append(files)


    pygame.mixer.init()
    pygame.mixer.music.load(listofsongs[0])
    pygame.mixer.music.play()

directorychooser()

def updatelabel():
    global index
    global songname
    v.set(realnames[index])
    #return songname

def nextsong():
    global index
    index += 1
    pygame.mixer.music.load(listofsongs[index])
    pygame.mixer.music.play()
    updatelabel()

def prevsong():
    global index
    index -= 1
    pygame.mixer.music.load(listofsongs[index])
    pygame.mixer.music.play()
    updatelabel()


def pause():
    pygame.mixer.music.pause()
    v.set("")
    #return songname

def unpause():
    pygame.mixer.music.unpause()
    v.set("")


cap = cv2.VideoCapture(0)
while(cap.isOpened()):
    # read image
    ret, img = cap.read()

    # get hand data from the rectangle sub window on the screen
    cv2.rectangle(img, (300,300), (100,100), (0,255,0),0)
    crop_img = img[100:300, 100:300]

    # convert to grayscale
    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    # applying gaussian blur
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)

    # thresholdin: Otsu's Binarization method
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    # show thresholded image
    cv2.imshow('Thresholded', thresh1)

    # check OpenCV version to avoid unpacking error
    (version, _, _) = cv2.__version__.split('.')

    if version == '3':
        image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
                                                      cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    elif version == '2':
        contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, \
                                               cv2.CHAIN_APPROX_NONE)

    # find contour with max area
    cnt = max(contours, key = lambda x: cv2.contourArea(x))

    # create bounding rectangle around the contour (can skip below two lines)
    x, y, w, h = cv2.boundingRect(cnt)
    cv2.rectangle(crop_img, (x, y), (x+w, y+h), (0, 0, 255), 0)

    # finding convex hull
    hull = cv2.convexHull(cnt)

    # drawing contours
    drawing = np.zeros(crop_img.shape,np.uint8)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
    cv2.drawContours(drawing, [hull], 0,(0, 0, 255), 0)

    # finding convex hull
    hull = cv2.convexHull(cnt, returnPoints=False)

    # finding convexity defects
    defects = cv2.convexityDefects(cnt, hull)
    count_defects = 0
    cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

    # applying Cosine Rule to find angle for all defects (between fingers)
    # with angle > 90 degrees and ignore defects
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]

        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])

        # find length of all sides of triangle
        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

        # apply cosine rule here
        angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

        # ignore angles > 90 and highlight rest with red dots
        if angle <= 90:
            count_defects += 1
            cv2.circle(crop_img, far, 1, [0,0,255], -1)
        #dist = cv2.pointPolygonTest(cnt,far,True)

        # draw a line from start to end i.e. the convex points (finger tips)
        # (can skip this part)
        cv2.line(crop_img,start, end, [0,255,0], 2)
        #cv2.circle(crop_img,far,5,[0,0,255],-1)

    # define actions required

    if count_defects == 1:
        cv2.putText(img,"Play Song", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        try:
            unpause()
        except:
            print "There are no more songs"

    elif count_defects == 2:
        cv2.putText(img,"Pause", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        pause()
    elif count_defects == 3:
        cv2.putText(img,"Pause", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        pause()

    # elif count_defects == 3:
    #     print "Four fingers."
    #     str = "Next Song"
    #     cv2.putText(img, str, (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    #     try:
    #         nextsong()
    #     except:
    #         print "There are no more next songs"
    #
    # elif count_defects == 3:
    #     cv2.putText(img,"Previous Song", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
    #     try:
    #         prevsong()
    #     except:
    #         print "There are not previous songs."


    elif count_defects == 4:
        cv2.putText(img,"Pause", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        pause()
    else:
        cv2.putText(img,"No option given. Playing!!!", (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 2, 2)

    # show appropriate images in windows
    cv2.imshow('Gesture', img)
    all_img = np.hstack((drawing, crop_img))
    cv2.imshow('Contours', all_img)

    k = cv2.waitKey(10)
    if k == 27:
        break

    # time.sleep(0.2)
