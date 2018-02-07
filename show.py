from enum import Enum

from blink_detector import Facer
from blinking_show import BlinkingShow
from video_streamer import VideoStreamer
from osc_client import OSCClient
import time #??

# blink_detector = BlinkDetector()
# blink_detector.calibrate(CurrentEAR)
# take frames ear at calibrate state. Take min, max
# blink_detector.stop_calibrator()
# blink_detector.detect()

class Scene(Enum):
    INIT = 0
    CALIBRATING = 1
    START = 2
    END = 3

class Show:
    def __init__(self, ip, port, predictor):
        self.ip = ip
        self.port = port
        self.predictor = predictor
        self.scene = Scene.INIT
    
    @property
    def current_scene(self):
        return self.scene

    def run(self):
        print("[INFO] loading facial landmark predictor...")
        detector = Facer(self.predictor)

        # start the video stream thread
        print("[INFO] camera sensor warming up...")
        vs = VideoStreamer()
        vs.run()

        # OSC client
        osc_client = OSCClient(self.ip, self.port)
        time.sleep(2.0)

        while True:
            if self.scene == Scene.START:
                print("Its show time...")
                osc_client.send("/scene", Scene.START.value)
                self.start_scene(vs, detector, osc_client, self.no_one_in)

            if self.scene == Scene.CALIBRATING:
                print("Calibrating...")
                osc_client.send("/scene", Scene.CALIBRATING.value)
                self.calibrating_scene()
            
            if self.scene == Scene.INIT:
                print("This is init")
                osc_client.send("/scene", Scene.INIT.value)
                # self.scene = Scene.START
                self.scene = Scene.CALIBRATING
            
            if self.scene == Scene.END:
                print("This is the end")
                osc_client.send("/scene", Scene.END.value)
            
        # do a bit of cleanup
        vs.stop()
    
    def start_scene(self, vs, detector, osc_client, no_one_in):
        blinking_show = BlinkingShow(vs, detector, osc_client, self.no_one_in)
        timer = Timer()
        # counter = 0
        start_time = int(time.time())
        while True:
            print("Show timer", timer.value())
            # print("Counter", counter)
            blinking_show.run()
            if timer.value() > 30:
                self.scene = Scene.CALIBRATING
                break
            # counter += 1
    
    def no_one_in(self):
        print("No one in =(")
        self.scene = Scene.INIT
        return
    
    def calibrating_scene(self):
        timer = Timer()
        while True:
            print("Calibration timer", timer.value())
            if timer.value() > 10:
                self.scene = Scene.START
                break
    
    def init_scene(self):
        return

class Timer:
    def __init__(self):
        self.started_at = int(time.time())

    def value(self):
        return int(time.time()) - self.started_at