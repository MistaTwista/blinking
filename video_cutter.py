import cv2

vidcap = cv2.VideoCapture('madmax.mov');
success, image = vidcap.read()
count = 0
success = True

while success:
    success, image = vidcap.read()
    if count % 200 == 0:
        cv2.imwrite("frame%d.jpg" % count, image)
    print('success')
    count += 1
