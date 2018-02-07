import cv2
from blink_detector import FaceRecognizer
import eye

class Calibrator:
    # after this count of frames without eye - stop
    RESET_THRESH = 100

    # Frames without person
    NO_ONE_IN = 0

    EAR_MIN = 0.1
    EAR_MAX = 4

    ALREADY_STOP = False

    def __init__(self, video_stream, detector, calibrated_cb, no_one_in_cb):
        self.video_stream = video_stream
        self.detector = detector
        self.calibrated_cb = calibrated_cb
        self.no_one_in = no_one_in_cb
        self.show_debug = True
        self.run()
    
    def run(self):
        # take frame from stream
        self.frame = self.video_stream.get_frame()
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = self.detector.detect(gray)

        self.detect_nobody(rects)
        self.ear = 0

        # loop over the face detections
        for rect in rects:
            # extract face shapes
            shapes = self.detector.get_shapes(gray, rect)
            self.ear = self.detect_ear(shapes, self.show_debug)
            # save somehow data to EAR_MIX & EAR_MAX

        if self.show_debug:
            cv2.putText(self.frame, "EAR: {:.2f}".format(self.ear), (200, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # show the frame
        cv2.imshow("Frame", self.frame)

    def stop(self):
        if not self.ALREADY_STOP:
            self.ALREADY_STOP = True
            cv2.destroyAllWindows()
            self.calibrated_cb(0.24)
    
    def data(self):
        return [self.EAR_MIN, self.EAR_MAX]

    def detect_nobody(self, rects):
        if len(rects) < 1:
            self.NO_ONE_IN += 1
        else:
            self.NO_ONE_IN = 0
        
        if self.NO_ONE_IN > self.RESET_THRESH:
            self.stop()

        if self.show_debug:
            cv2.putText(self.frame, "NO_ONE_IN: {:.2f}".format(self.NO_ONE_IN), (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def detect_ear(self, shapes, show_contour = True):
        # extract eye ear
        # rightEye = FaceRecognizer.right_eye(shapes) # TODO: Bad name facerecognizer
        leftEye = FaceRecognizer.left_eye(shapes) # TODO: Bad name facerecognizer
        # compute the convex hull for an eye, then visualize
        # rightEyeHull = cv2.convexHull(rightEye)
        leftEyeHull = cv2.convexHull(leftEye)
        # rightEAR = eye.aspect_ratio(rightEye)
        leftEAR = eye.aspect_ratio(leftEye)
        # average the eye aspect ratio together for both eyes
        # ear = (leftEAR + rightEAR) / 2.0
        ear = leftEAR
        if show_contour:
            # cv2.drawContours(self.frame, [rightEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(self.frame, [leftEyeHull], -1, (0, 255, 0), 1)
        
        return ear
