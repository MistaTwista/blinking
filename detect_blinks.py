import eye
# from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils

from pythonosc import osc_message_builder
from pythonosc import udp_client

import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

EYE_AR_THRESH = 0.24
EYE_AR_CONSEC_FRAMES = 1

# after this count of frames without eye - reset CURRENT_SCENE to 0
RESET_THRESH = 50

# Scene 0 - reset scene
# Scene 1 - calibration scene / intro
# Scene 2 - movie
# Scene 3 - outro
# enum?
CURRENT_SCENE = 0

# Frames without person
NO_ONE_IN = 0


ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
ap.add_argument("--ip", default="127.0.0.1", help="OSC server IP")
ap.add_argument("--port", type=int, default=5005, help="OSC server port")
args = ap.parse_args()


# initialize the frame counters and the total number of blinks
COUNTER = 0
TOTAL = 0
FRAME_COUNTER = 0

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args.shape_predictor)

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
# (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] camera sensor warming up...")
vs = VideoStream().start()

# OSC client
client = udp_client.SimpleUDPClient(args.ip, args.port)

time.sleep(2.0)
counter = 0

start_time = int(time.time())
while True:
	print("Counter:", counter)
	CURRENT_SCENE = 1
	# grab video, resize and convert it to grayscale
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# grayed = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# detect faces in the grayscale frame
	rects = detector(gray, 0)

	# if there is no rects for 5 seconds - reset
	# if len(rects) > 0:
	# 	client.send_message("/reset", 1)
	# 	time.sleep(0.2)
	# 	client.send_message("/reset", 0)

	# loop over the face detections
	for rect in rects:
		# determine the facial landmarks for the face region, then
		# convert the facial landmark (x, y)-coordinates to a NumPy
		# array
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)

		# extract the left and right eye coordinates, then use the
		# coordinates to compute the eye aspect ratio for both eyes
		# leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		# leftEAR = eye.aspect_ratio(leftEye)
		rightEAR = eye.aspect_ratio(rightEye)

		# average the eye aspect ratio together for both eyes
		# ear = (leftEAR + rightEAR) / 2.0

		# compute the convex hull for the left and right eye, then
		# visualize each of the eyes
		# leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		# cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

		# check to see if the eye aspect ratio is below the blink
		# threshold, and if so, increment the blink frame counter
		if rightEAR < EYE_AR_THRESH:
			COUNTER += 1

		# otherwise, the eye aspect ratio is not below the blink
		# threshold
		else:
			# if the eyes were closed for a sufficient number of
			# then increment the total number of blinks
			if COUNTER >= EYE_AR_CONSEC_FRAMES:
				TOTAL += 1

			# reset the eye frame counter
			COUNTER = 0

		# draw the total number of blinks on the frame along with
		# the computed eye aspect ratio for the frame
		client.send_message("/counter", TOTAL)
		client.send_message("/ear", rightEAR)

		cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
		cv2.putText(frame, "EAR: {:.2f}".format(rightEAR), (200, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

	cv2.putText(frame, "Rect: {:.2f}".format(len(rects)), (10, 60),
		cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	cv2.putText(frame, "Frame: {:.2f}".format(FRAME_COUNTER), (10, 90),
		cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

	if len(rects) < 1:
		NO_ONE_IN += 1
	else:
		NO_ONE_IN = 0
	
	if NO_ONE_IN > RESET_THRESH:
		CURRENT_SCENE = 0

	cv2.putText(frame, "NO_ONE_IN: {:.2f}".format(NO_ONE_IN), (10, 120),
		cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	cv2.putText(frame, "CURRENT_SCENE: {:.2f}".format(CURRENT_SCENE), (10, 150),
		cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


	FRAME_COUNTER += 1
	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
	
	counter += 1
	seconds_from_start = int(time.time()) - start_time
	print(seconds_from_start)

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

