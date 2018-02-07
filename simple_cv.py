import numpy as np
import cv2
import time

cap = cv2.VideoCapture(0)
counter = 0

start_time = int(time.time())
if cap.isOpened():
	while True:
		print("Counter", counter)
		check, frame = cap.read()
		cv2.imshow('frame',frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		counter += 1
		print(int(time.time()) - start_time)

cap.release()
cv2.destroyAllWindows()
