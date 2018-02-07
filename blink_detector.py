import dlib
from imutils import face_utils

class Facer:
    def __init__(self, predictor_path):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)
    
    def get_shapes(self, frame, rect):
        shapes = self.__predict(frame, rect)
        return face_utils.shape_to_np(shapes) # convert dlib shapes to numpy format

    def detect(self, frame, resample_count = 0):
        return self.detector(frame, resample_count)
    
    def __predict(self, frame, rect):
        return self.predictor(frame, rect)

class FaceRecognizer:
    @staticmethod
    def right_eye(shape):
        (r_start, r_end) = FaceRecognizer.__right_eye()
        return shape[r_start:r_end]
    
    @staticmethod
    def left_eye(shape):
        (l_start, l_end) = FaceRecognizer.__left_eye()
        return shape[l_start:l_end]

    @staticmethod
    def __right_eye():
        return face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
    
    @staticmethod
    def __left_eye():
        return face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    