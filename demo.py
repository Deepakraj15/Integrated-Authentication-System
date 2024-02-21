import face_recognition
image = face_recognition.load_image_file("Deepakraj_K.jpeg")
capture = face_recognition.load_image_file("./CapturedImage/Benjamin.jpg")
encoding1 = face_recognition.face_encodings(image)[0]
encoding2 = face_recognition.face_encodings(capture)[0]
results = face_recognition.compare_faces([encoding1],encoding2)
print(results)