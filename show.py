from enum import Enum

from blink_detector import Facer
from blinking_show import BlinkingShow
from eye_detector import EyeDetector
from calibrator import Calibrator
from video_streamer import VideoStreamer
from osc_client import OSCClient
import time

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
    
    def run(self):
        print("[INFO] loading facial landmark predictor...")
        detector = Facer(self.predictor)

        # start the video stream thread
        print("[INFO] camera sensor warming up...")
        vs = VideoStreamer()
        vs.run()

        # OSC client
        osc_client = OSCClient(self.ip, self.port)
        # time.sleep(2.0)

        while True:
            if self.scene == Scene.INIT:
                print("This is init")
                osc_client.send("/scene", Scene.INIT.value)
                self.init_scene(vs, detector)

            if self.scene == Scene.CALIBRATING:
                print("Calibrating...")
                osc_client.send("/scene", Scene.CALIBRATING.value)
                self.calibrating_scene(vs, detector)

            if self.scene == Scene.START:
                print("Its show time...")
                osc_client.send("/scene", Scene.START.value)
                self.start_scene(vs, detector, osc_client, self.no_one_in)

            if self.scene == Scene.END:
                print("This is the end")
                osc_client.send("/scene", Scene.END.value)
                self.end_scene()

        # do a bit of cleanup
        vs.stop()

    def init_scene(self, vs, detector):
        detector = EyeDetector(vs, detector, self.person_find)
        timer = Timer()
        while True:
            print("Init timer", timer.value())
            detector.run()
            if self.scene == Scene.CALIBRATING:
                break

    def calibrating_scene(self, vs, detector):
        calibrator = Calibrator(vs, detector, self.calibrated, self.no_one_in)
        timer = Timer()
        while True:
            print("Calibration timer", timer.value())
            calibrator.run()
            if timer.value() > 16:
                calibrator.stop()
                self.scene = Scene.START
                break
    
    def start_scene(self, vs, detector, osc_client, no_one_in):
        blinking_show = BlinkingShow(vs, detector, osc_client, self.no_one_in)
        timer = Timer()
        while True:
            print("Show timer", timer.value())
            blinking_show.run()
            if timer.value() > 54:
                self.scene = Scene.END
                break
    
    def end_scene(self):
        timer = Timer()
        while True:
            print("End timer", timer.value())
            if timer.value() > 5:
                self.scene = Scene.INIT
                break
    
    def calibrated(self, threshold):
        print("Calibrated")
        self.scene = Scene.START
        self.BLINK_THRESHOLD = threshold
        return

    # Runs when finder find a person
    def person_find(self):
        print("PERSON!")
        self.scene = Scene.CALIBRATING
        return

    def no_one_in(self):
        print("No one in =(")
        self.scene = Scene.INIT
        return

class Timer:
    def __init__(self):
        self.started_at = int(time.time())

    def value(self):
        return int(time.time()) - self.started_at