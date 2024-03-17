from io import BytesIO
from flask import Flask,render_template,Response,request,jsonify
from pymongo import MongoClient
import tensorflow as tf
import numpy as np
import cv2
import dlib
import base64
import time
import os
import face_recognition
import qrcode

app = Flask(__name__)

global name,data1,data2

client = MongoClient("<place your own url>")
db = client["project"]
collection = db["mobileapp"]

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
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=15,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(qr_img, format="PNG")
    qr_img.seek(0)
    qr_img_base64 = base64.b64encode(qr_img.getvalue()).strip()


    return render_template('qrcode.html', qr_img_base64=qr_img_base64.decode())

@app.route('/verifypin',methods=['POST'])
def verify_pin():
    data = request.json
    result = collection.find_one(data)
    if(result):
        send_success_response()
        render_template('signature_verfication.html')
    else:
        return jsonify({"message":"Error"}),500

def send_success_response():
    return jsonify({"message":"Success"}),200

@app.route('/signature_verification')
def signature_verification():
    return render_template('sign.html')

@app.route('/predict', methods=['POST'])
def classify_strokes():
    data = request.json  
    model = tf.keras.models.load_model('./models/Best_RNN_model.h5')
    coordinates = [float(coord_str) for coord_pair in data for coord_str in coord_pair.split(',')]
    test_XX = np.expand_dims(coordinates, axis=-1)
    predictions = model.predict(test_XX)
    predicted_labels = (predictions > 0.5).astype(int)
    check_stroke_prediction(predicted_labels)
    return jsonify({'message':'prediction'})

@app.route('/process_signature_image',methods =['POST'])
def classify_image():
    try:
        model = tf.keras.models.load_model('./models/model1.h5')
        data = request.json
        image_data = data.get('image_data')    
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        signature_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        resized_image = cv2.resize(signature_image, (256, 256))
        img_array = np.expand_dims(resized_image, axis=0)  
        img_array = img_array.astype('float32') / 255.0
        predictions = model.predict(img_array)
        check_image_prediction(predictions[0])
        return jsonify({'message': 'success'})
    except Exception as e:
        return jsonify({'error': 'Something went wrong'})
@app.route('/results')
def render_results():
    if(data1 and data2):
        data = True
    elif(data2):
        data = True
    else:
        data = False
    return render_template('sign_update.html',data = data)

def check_image_prediction(predictions):
    global data2
    print(predictions)
    if(predictions[1]>0.6):
        data2  = True
    else:
        data2 = False
    print(data2)
def check_stroke_prediction(predicted_labels):
    global data1
    w_count,r_count = 0,0
    for label in predicted_labels:
        if(label[0] == 1):
            w_count +=1
        if(label[1] == 1):
            r_count +=1
    if(r_count > w_count):
        data1 = True
    else:
        data1 = False
    print("["+str(w_count)+","+str(r_count)+"]")
