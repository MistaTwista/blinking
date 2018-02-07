from show import Show
import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
ap.add_argument("--ip", default="127.0.0.1", help="OSC server IP")
ap.add_argument("--port", type=int, default=5005, help="OSC server port")
args = ap.parse_args()

show = Show(args.ip, args.port, args.shape_predictor)
show.run()