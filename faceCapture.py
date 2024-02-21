import cv2
import dlib

def faceCapture():
    detector = dlib.get_frontal_face_detector()

    predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")
    name = input("Enter your name: ")
    cap = cv2.VideoCapture(0)

    while True:

        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)
        if ret:
            cv2.imshow("My Screen", frame)

        key = cv2.waitKey(1)
        if key == ord("q"):
            cv2.imwrite("./CapturedImage/{0}.jpg".format(name),frame) # to save image
            
            break

    cap.release()
    cv2.destroyAllWindows()

faceCapture()