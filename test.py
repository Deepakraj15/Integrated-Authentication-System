import os
import cv2
names = os.listdir('./CapturedImage')
for name in names:
    print(name.split(".")[0])