# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from datetime import datetime
import numpy as np
import time
import cv2
import cv2.cv as cv


kernel = np.ones((5,5),np.uint8)

def nothing(x):
    pass

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
#camera.resolution = (2592,1944)
#camera.set(15,100)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
#rawCapture = PiRGBArray(camera, size=(2592,1944))

# allow the camera to warmup
time.sleep(0.1)

# open  new window with hue
cv2.namedWindow('HueComp')
#cv2.namedWindow('spot')
cv2.createTrackbar('hmin', 'HueComp',12,179,nothing)
cv2.createTrackbar('hmax', 'HueComp',37,179,nothing)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array
	hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
	hue,sat,val = cv2.split(hsv)

	# get info from track bar and appy to result
	hmn = cv2.getTrackbarPos('hmin','HueComp')
	hmx = cv2.getTrackbarPos('hmax','HueComp')

	# Apply thresholding
	hthresh = cv2.inRange(np.array(hue),np.array(hmn),np.array(hmx))

	# Some morpholigical filtering
	dilation = cv2.dilate(hthresh,kernel,iterations = 1)
	closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel)
	closing = cv2.GaussianBlur(closing,(5,5),0)

	# Detect circles using HoughCircles
	circles = cv2.HoughCircles(closing,cv.CV_HOUGH_GRADIENT,2,120,param1=120,param2=50,minRadius=60,maxRadius=0)

	#Draw Circles
	if circles is not None:
		for i in circles[0,:]:
			cv2.circle(image,(int(round(i[0])),int(round(i[1]))),int(round(i[2])),(0,255,0),5)
			cv2.circle(image,(int(round(i[0])),int(round(i[1]))),2,(0,255,0),10)
			print('radius: {}'.format(i[2]))	

	# show the frame
	cv2.imshow("Frame", image)
	cv2.imshow('HueComp', hthresh)

	#cv2.imshow('spot', closing)

	key = cv2.waitKey(1) & 0xFF
	
	if key == ord('i'):
        	cv2.imwrite('pic'+datetime.now().strftime("%Y-%d-%m_%Hh%Mm%Ss")+'.png', image)	
		camera.brightness = 100
		time.sleep(.5)
		camera.brightness = 50
	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
