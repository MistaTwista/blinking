from scipy.spatial import distance as dist

# Compute the euclidean distances between vertical and horisontal landmarks
def aspect_ratio(eye):
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
	# horizontal eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	ear = (A + B) / (2.0 * C)
	return ear
