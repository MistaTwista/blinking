import cv2
from blink_detector import FaceRecognizer
import eye
import time

class BlinkingShow:
    EYE_AR_THRESH = 0.24
    EYE_AR_CONSEC_FRAMES = 1

    # after this count of frames without eye - reset CURRENT_SCENE to 0
    RESET_THRESH = 50

    # initialize the frame counters and the total number of blinks
    COUNTER = 0
    TOTAL = 0
    FRAME_COUNTER = 0

    # Frames without person
    NO_ONE_IN = 0

    def __init__(self, video_stream, detector, osc_client, no_one_in):
        self.video_stream = video_stream
        self.detector = detector
        self.osc_client = osc_client
        self.no_one_in = no_one_in
        self.show_debug = False
        self.run()
    
    def run(self):
        counter = 0
        start_time = int(time.time())
        while True:
            print("Counter", counter)
            # take frame from stream
            self.frame = self.video_stream.get_frame()
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            # detect faces in the grayscale frame
            rects = self.detector.detect(gray)

            self.detect_nobody(rects)
            self.ear = 0

            # if self.show_debug:
            #     cv2.putText(frame, "CURRENT_SCENE: {:.2f}".format(self.CURRENT_SCENE), (10, 150),
            #         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # loop over the face detections
            for rect in rects:
                # extract face shapes
                shapes = self.detector.get_shapes(gray, rect)
                self.ear = self.detect_ear(shapes, self.show_debug)
                self.detect_blink()

            self.run_every_frame(rects)
            self.osc_client.send("/ear", self.ear)

            if self.show_debug:
                cv2.putText(self.frame, "EAR: {:.2f}".format(self.ear), (200, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # show the frame
            cv2.imshow("Frame", self.frame)
            counter += 1
            seconds_from_start = int(time.time()) - start_time
            print(seconds_from_start)

    def reset(self):
        cv2.destroyAllWindows()
        self.no_one_in()

    def detect_nobody(self, rects):
        if len(rects) < 1:
            self.NO_ONE_IN += 1
        else:
            self.NO_ONE_IN = 0
        
        if self.NO_ONE_IN > self.RESET_THRESH:
            self.reset()
            # self.CURRENT_SCENE = 0

        if self.show_debug:
            cv2.putText(self.frame, "NO_ONE_IN: {:.2f}".format(self.NO_ONE_IN), (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def detect_blink(self):
        if self.ear < self.EYE_AR_THRESH:
            # increment counter of closed eye
            self.COUNTER += 1
        else:
            # if the eyes were closed for a sufficient number of frames
            if self.COUNTER >= self.EYE_AR_CONSEC_FRAMES:
                # there was a blink
                self.TOTAL += 1
                self.was_blinked()

            # reset the eye frame counter
            self.COUNTER = 0


    def detect_ear(self, shapes, show_contour = True):
        # extract eye ear
        rightEye = FaceRecognizer.right_eye(shapes) # TODO: Bad name facerecognizer
        # compute the convex hull for an eye, then visualize
        rightEyeHull = cv2.convexHull(rightEye)
        rightEAR = eye.aspect_ratio(rightEye)
        # average the eye aspect ratio together for both eyes
        # ear = (leftEAR + rightEAR) / 2.0
        if show_contour:
            cv2.drawContours(self.frame, [rightEyeHull], -1, (0, 255, 0), 1)
        
        return rightEAR

    def run_every_frame(self, rects):
        # async check key for exit
        key = cv2.waitKey(1) & 0xFF
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            self.reset()

        if self.show_debug:
            cv2.putText(self.frame, "Blinks: {}".format(self.TOTAL), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(self.frame, "Rect: {:.2f}".format(len(rects)), (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(self.frame, "Frame: {:.2f}".format(self.FRAME_COUNTER), (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        self.FRAME_COUNTER += 1

    def was_blinked(self):
        self.osc_client.send("/counter", self.TOTAL)