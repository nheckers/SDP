from flask import Flask, render_template, Response
import cv2
import pickle
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime

app = Flask(__name__)

class FacialLoginSystem:
    def __init__(self):
        self.init_firebase()
        self.setup_camera()
        self.load_encodings()
        self.user_states = {}
        self.LOGIN_TIMEOUT = 30

    def init_firebase(self):
        cred = credentials.Certificate("serviceAccountKey.json")
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {
                'databaseURL': "https://sdp2024-6ca30-default-rtdb.firebaseio.com/"
            })

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 700)  # Width
        self.cap.set(4, 500)  # Height

    def load_encodings(self):
        print("Loading Encoding file...")
        with open('EncodeFile.p', 'rb') as file:
            self.encodeListKnownWithIds = pickle.load(file)
        self.encodeListKnown, self.personIds = self.encodeListKnownWithIds
        print("Encode File Loaded")

    def process_frame(self, frame):
        """Process frame and add recognition boxes"""
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(imgS)
        
        for top, right, bottom, left in face_locations:
            # Scale back up face locations
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Get face encoding
            face_encoding = face_recognition.face_encodings(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                                                          [(top, right, bottom, left)])[0]
            
            # Check if face is known
            matches = face_recognition.compare_faces(self.encodeListKnown, face_encoding)
            
            if True in matches:
                matchIndex = np.argmin(face_recognition.face_distance(self.encodeListKnown, face_encoding))
                person_id = self.personIds[matchIndex]
                
                # Draw green box and name for known person
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, person_id, (left + 6, bottom - 6), 
                          cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            else:
                # Draw red box for unknown person
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, 'Unknown', (left + 6, bottom - 6),
                          cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return frame

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()

# Initialize the system
facial_system = FacialLoginSystem()

def generate_frames():
    while True:
        success, frame = facial_system.cap.read()
        if not success:
            break
        
        # Process frame with face detection
        output_frame = facial_system.process_frame(frame)
        
        # Convert frame to jpg
        ret, buffer = cv2.imencode('.jpg', output_frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(debug=False, port=5000)
    except KeyboardInterrupt:
        facial_system.cleanup()