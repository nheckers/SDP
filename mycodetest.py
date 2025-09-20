#!/usr/bin/python3

import cv2
import pickle
import face_recognition
import numpy as np
from datetime import datetime
import sqlite3
from scipy.spatial import distance as dist
from imutils import face_utils
import dlib
import os
import time
import getpass
import kwikset


class FacialLoginSystem:
    def __init__(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('SDP.db')
        self.cursor = self.conn.cursor()

        # Prompt for username and password
        self.authenticate_user()

        # Prompt user to select a room
        self.select_room()

        # Initialize Kwikset lock system
        self.kwikset = kwikset
        self.kwikset.setup_serial()
        self.kwikset.setup_arduinobreakout_pins()
        self.kwikset.lock()  # Lock the door at startup
        self.lock_state = "locked"  # Initial state

        # Camera and face recognition setup
        self.setup_camera()
        self.load_encodings()

        # Initialize internal state
        self.user_states = {}
        self.face_visible = False
        self.LOGIN_TIMEOUT = 30
        self.detected_fake_faces = set()
        self.selected_room = None

        # Blink detection thresholds
        self.EYE_AR_THRESH = 0.3
        self.EYE_AR_CONSEC_FRAMES = 3
        self.blink_counters = {}  # Per-person blink tracking

        # Facial landmark model setup
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(r"C:\\Users\\punkp\\Desktop\\School\\SDP\\shape_predictor_68_face_landmarks.dat")

        # Eye index constants
        self.LEFT_EYE_START = 42
        self.LEFT_EYE_END = 48
        self.RIGHT_EYE_START = 36
        self.RIGHT_EYE_END = 42

        # Drawing colors for face box
        self.AUTHORIZED_COLOR = (0, 255, 0)    # Green
        self.UNAUTHORIZED_COLOR = (0, 0, 255)  # Red
        self.SPOOF_COLOR = (255, 0, 255)       # Purple

    def authenticate_user(self):
        """Prompt the user for a username and password and verify with the database."""
        print("Please log in before selecting a room:")
        while True:
            username = input("Username: ")
            password = getpass.getpass("Password: ")

            self.cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
            result = self.cursor.fetchone()

            if result:
                print(f"Login successful. Welcome, {username}.")
                break
            else:
                print("Invalid username or password. Please try again.")

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 700)  # Width
        self.cap.set(4, 500)  # Height
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

    def load_encodings(self):
        print("Loading Encoding file...")
        with open('EncodeFile.p', 'rb') as file:
            self.encodeListKnownWithIds = pickle.load(file)
        self.encodeListKnown, self.personIds = self.encodeListKnownWithIds
        print("Encode File Loaded")

    def select_room(self):
        self.cursor.execute('SELECT Room_No, Room_Name FROM Resources')
        rooms = self.cursor.fetchall()

        print("Select the room you are entering:")
        for room_id, room_name in rooms:
            print(f"{room_id}: {room_name}")

        while True:
            try:
                room_id = int(input("Enter room number: "))
                room_name = next((name for id_, name in rooms if id_ == room_id), None)
                if room_name:
                    self.selected_room = room_name
                    self.selected_room_id = room_id
                    print(f"Room selected: {self.selected_room}")
                    break
                else:
                    print("Invalid room number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

def eye_aspect_ratio(self, eye):
        """
        Calculate the eye aspect ratio
        """
        # Compute the euclidean distances between the vertical eye landmarks
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # Compute the euclidean distance between the horizontal eye landmarks
        C = dist.euclidean(eye[0], eye[3])

        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear

def detect_blink(self, frame, face_location, face_id):
        """
        Detect if the person is blinking, tracking separately for each face
        """
        # Initialize blink counters for this face if not already present
        if face_id not in self.blink_counters:
            self.blink_counters[face_id] = {
                'counter': 0,
                'total': 0
            }
            
        top, right, bottom, left = face_location
        rect = dlib.rectangle(left, top, right, bottom)
        
        # Determine the facial landmarks
        shape = self.predictor(frame, rect)
        shape = face_utils.shape_to_np(shape)
        
        # Extract the left and right eye coordinates
        leftEye = shape[self.LEFT_EYE_START:self.LEFT_EYE_END]
        rightEye = shape[self.RIGHT_EYE_START:self.RIGHT_EYE_END]
        
        # Calculate the eye aspect ratio for both eyes
        leftEAR = self.eye_aspect_ratio(leftEye)
        rightEAR = self.eye_aspect_ratio(rightEye)
        
        # Average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0
        
        # Check if eye aspect ratio is below the threshold
        if ear < self.EYE_AR_THRESH:
            self.blink_counters[face_id]['counter'] += 1
        else:
            # If the eyes were closed for a sufficient number of frames,
            # increment the total number of blinks
            if self.blink_counters[face_id]['counter'] >= self.EYE_AR_CONSEC_FRAMES:
                self.blink_counters[face_id]['total'] += 1
            self.blink_counters[face_id]['counter'] = 0
            
        return self.blink_counters[face_id]['total'] > 0

def get_user_role(self, person_id):
        """Get the role of a user based on their ID."""
        self.cursor.execute('SELECT Roles FROM Roles WHERE id=?', (person_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

def check_access(self, role, room_id):
        """Check if a role has access to a specific room."""
        self.cursor.execute('SELECT * FROM Rules WHERE Role=? AND Room_No=?', (role, room_id))
        return bool(self.cursor.fetchone())

def check_time_access(self, role):
        """Check if the role is allowed access based on the current time."""
        current_day = datetime.now().strftime("%A")
        current_time = datetime.now().strftime("%H:%M")

        self.cursor.execute(
            '''
            SELECT * FROM TimeRules 
            WHERE role_name=? AND day=? AND ? >= start_time
            ''', 
            (role, current_day, current_time)
        )
        return bool(self.cursor.fetchone())

def can_login(self, person_id):
        """Check if a person can attempt to login based on timeout."""
        if person_id not in self.user_states:
            return True

        user_state = self.user_states[person_id]
        if not user_state.get('last_login_time'):
            return True

        seconds_elapsed = (datetime.now() - user_state['last_login_time']).total_seconds()
        return seconds_elapsed > self.LOGIN_TIMEOUT

def test(self):
        print("Running test() to check and update lock state...")

        authorized_person = None
        latest_time = None

        for person_id, state in self.user_states.items():
            if state.get("has_access") and state.get("is_visible"):
                login_time = state.get("last_login_time")
                if login_time and (latest_time is None or login_time > latest_time):
                    latest_time = login_time
                    authorized_person = person_id

        if authorized_person:
            if self.lock_state != "unlocked":
                print(f"Access granted for {authorized_person}. Unlocking the door...")
                kwikset.unlock()
                self.lock_state = "unlocked"
            else:
                print("Already unlocked. No action taken.")
        else:
            if self.lock_state != "locked":
                print("Access denied or no authorized user visible. Locking the door...")
                kwikset.lock()
                self.lock_state = "locked"
            else:
                print("Already locked. No action taken.")


def process_login(self, person_id):
        """Process login with ABAC check."""
        if self.can_login(person_id):
            role = self.get_user_role(person_id)
            if not role:
                return False

            has_room_access = self.check_access(role, self.selected_room_id)
            has_time_access = self.check_time_access(role)
            has_access = has_room_access and has_time_access
            
            login_time = datetime.now()
            formatted_time = login_time.strftime("%d-%m-%Y %H:%M:%S")

            if person_id not in self.user_states:
                access_status = "GRANTED" if has_access else "DENIED"
                print(f"\nAccess {access_status} for user {person_id} ({role}) to {self.selected_room}")
            
            if has_access:
                print(f"\nAt {formatted_time}")
            
                

            self.user_states[person_id] = {
                'last_login_time': datetime.now(),
                'is_visible': True,
                'has_access': has_access,
                'role': role,
                'entry_time': formatted_time if has_access else None
            }
        
            return has_access


        return self.user_states[person_id].get('has_access', False)

def detect_faces(self, frame):
        """Detect and process faces in the frame."""
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(imgS)
        for person_id in self.user_states:
            self.user_states[person_id]['is_visible'] = False

        if face_locations:
            encodeCurFrame = face_recognition.face_encodings(imgS, face_locations)
            original_face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                                     for top, right, bottom, left in face_locations]

            for encodeFace, face_loc in zip(encodeCurFrame, original_face_locations):
                # Check for matches with known faces
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                
                if True in matches:
                    faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                    matchIndex = np.argmin(faceDis)
                    person_id = self.personIds[matchIndex]
                    
                    # Use person_id as the face_id for blink tracking
                    is_real_face = self.detect_blink(frame, face_loc, person_id)
                    
                    if not is_real_face:
                        self.draw_face_box(frame, face_loc, False, person_id, is_spoof=True)
                        continue
                    
                    has_access = self.process_login(person_id)
                    self.draw_face_box(frame, face_loc, has_access, person_id)
                else:
                    # For unknown faces, use face location as a unique identifier
                    unknown_id = f"unknown_{face_loc[0]}_{face_loc[1]}_{face_loc[2]}_{face_loc[3]}"
                    is_real_face = self.detect_blink(frame, face_loc, unknown_id)
                    
                    if not is_real_face:
                        self.draw_face_box(frame, face_loc, False, None, is_spoof=True)
                    else:
                        self.draw_face_box(frame, face_loc, False)

def draw_face_box(self, frame, location, is_authorized, person_id=None, is_spoof=False):
        """Draw a box around the face with color indicating authorization status."""
        top, right, bottom, left = location
        
        if is_spoof:
            color = self.SPOOF_COLOR
            status_text = "FAKE FACE DETECTED"
        else:
            color = self.AUTHORIZED_COLOR if is_authorized else self.UNAUTHORIZED_COLOR
            status_text = f"{person_id} ({self.user_states[person_id]['role']})" if person_id and person_id in self.user_states else "Unauthorized"
        
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom + 35), (right, bottom), color, cv2.FILLED)
        
        # Add blink counter if not a spoof, using the person-specific counter
        face_id = person_id if person_id else f"unknown_{top}_{right}_{bottom}_{left}"
        if face_id in self.blink_counters:
            blink_text = f"Blinks: {self.blink_counters[face_id]['total']}"
            cv2.putText(frame, blink_text, (left, top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        font = cv2.FONT_HERSHEY_DUPLEX
        text_size = cv2.getTextSize(status_text, font, 0.6, 1)[0]
        text_x = left + (right - left - text_size[0]) // 2
        cv2.putText(frame, status_text, (text_x, bottom + 25), font, 0.6, (255, 255, 255), 1)

    

def run(self):
        """Main loop for running the facial recognition system."""
        print("Starting facial recognition system...")
        print("Press 'q' to quit.")

        while True:
            success, frame = self.cap.read()
            if not success:
                print("Failed to grab frame")
                break

            self.detect_faces(frame)

            
            if int(time.time()) % 5 == 0:
             self.test()

            cv2.imshow("Face Login System", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nShutting down system...")
                break

        self.cleanup()

def cleanup(self):
        """Clean up resources."""
        self.cap.release()
        cv2.destroyAllWindows()
        self.conn.close()

if __name__ == "__main__":
    login_system = FacialLoginSystem()
    login_system.run()
