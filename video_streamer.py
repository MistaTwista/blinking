from imutils.video import VideoStream
import imutils

class VideoStreamer():
    def __init__(self):
        self.stream = VideoStream()

    def run(self):
        self.stream.start()

    def get_frame(self):
        frame = self.stream.read()
        return imutils.resize(frame, width=400)
    
    def stop(self):
        self.stream.stop()