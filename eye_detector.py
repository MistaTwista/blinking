import cv2

class EyeDetector:
    ALREADY_STOP = False

    def __init__(self, video_stream, detector, someone_cb):
        self.video_stream = video_stream
        self.detector = detector
        self.someone_cb = someone_cb
        self.run()
    
    def run(self):
        # take frame from stream
        self.frame = self.video_stream.get_frame()
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = self.detector.detect(gray)

        print("Rects", len(rects))
        if len(rects) > 0:
            self.stop()

        # show the frame
        cv2.imshow("Frame", self.frame)

    def stop(self):
        if not self.ALREADY_STOP:
            self.ALREADY_STOP = True
            cv2.destroyAllWindows()
            self.someone_cb()
