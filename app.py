from io import BytesIO
from flask import Flask,render_template,Response,request,jsonify
from pymongo import MongoClient
import cv2
import dlib
import base64
import numpy as np
import time
import os
import face_recognition
import qrcode

app = Flask(__name__)

global name
def generate_frames():
    detector = dlib.get_frontal_face_detector()

    predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)

            for point in landmarks.parts():
                 cv2.circle(frame, (point.x, point.y), 1, (0, 0, 255),1,cv2.LINE_8)
           

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/")
def hello_world():
    return render_template("home.html")

@app.route('/video')
def video():
    return render_template('face.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process', methods=['POST'])
def captureandcompare():
    try:
        data = request.json
        image_data = data.get('image_data')    
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        capturedimage = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        imageslist = os.listdir('./CapturedImage')
        for image in imageslist:
           sourceimage = cv2.imread('./CapturedImage/'+image)
           encoding1 = face_recognition.face_encodings(sourceimage)[0]
           encoding2 = face_recognition.face_encodings(capturedimage)[0]
           result = face_recognition.compare_faces([encoding1],encoding2)
           print(result)
           if(result[0] == True):
               global name
               name  = image.split('.')[0]
               return jsonify({'message':'success'}),200
        return render_template('failure.html')
    except:
        return jsonify({'message': 'Internal error with the server'}),500

@app.route('/qrgenerator')
def qrgenerator():
    
    data = name

    # Generate QR code in memory
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=15,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create a BytesIO buffer to store the QR code image
    qr_img = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(qr_img, format="PNG")
    qr_img.seek(0)
    
    # Convert the QR code image to a base64-encoded string
    qr_img_base64 = base64.b64encode(qr_img.getvalue()).strip()


    return render_template('qrcode.html', qr_img_base64=qr_img_base64.decode())

@app.route('/verifypin',methods=['POST'])
def verify_pin():
    pass