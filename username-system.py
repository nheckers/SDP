import cv2
import pickle
import face_recognition
import numpy as np
from datetime import datetime
import sqlite3
import os
import bcrypt

class FacialLoginSystem:
    def __init__(self):
        self.setup_camera()
        self.load_encodings()
        self.user_states = {}
        self.face_visible = False
        self.LOGIN_TIMEOUT = 30
        self.unauthorized_message_shown = False
        self.selected_room = None
        
        #Colors for the boxes (in BGR format)
        self.AUTHORIZED_COLOR = (0, 255, 0)    # Green
        self.UNAUTHORIZED_COLOR = (0, 0, 255)   # Red
        
        #database connection
        self.conn = sqlite3.connect(r"C:\Users\punkp\Desktop\School\SDP\SDP.db")
        self.cursor = self.conn.cursor()
        
        self.select_room()
    

    def setup_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 700)
        self.cap.set(4, 500)
        
    def load_encodings(self):
        print("Loading Encoding file...")
        with open('EncodeFile.p', 'rb') as file:
            self.encodeListKnownWithIds = pickle.load(file)
        self.encodeListKnown, self.personIds = self.encodeListKnownWithIds
        print("Encode File Loaded")

    def select_room(self):
        """Prompt the user to select a room."""
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
    
    def verify_login(self):
     username = input("Enter your username: ")
     password = input("Enter your password: ")

     self.cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
     result = self.cursor.fetchone()

     if result:
        person_id, stored_hashed_password = result
        if bcrypt.checkpw(password.encode(), stored_hashed_password.encode()):
            print("Login successful.")
            return person_id
        else:
            print("Incorrect password.")
     else:
        print("Username not found.")

     return None

    def get_user_role(self, person_id):
        """Get the role of a user based on their ID."""
        self.cursor.execute('SELECT Roles FROM Roles WHERE id=?', (person_id,)) #takes the person's role based on the ID
        result = self.cursor.fetchone()
        return result[0] if result else None

    def check_access(self, role, room_id):
        """Check if a role has access to a specific room."""
        self.cursor.execute('SELECT * FROM Rules WHERE Role=? AND Room_No=?', (role, room_id)) 
        return bool(self.cursor.fetchone()) #Returns True if a matching rule exists, False otherwise

    def get_room_id(self, room_name):
        """Get room ID from room name."""
        self.cursor.execute('SELECT Room_No FROM Resources WHERE Room_Name=?', (room_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None #Returns None if the person isn't found in the database

    def can_login(self, person_id):
        if person_id not in self.user_states:
            return True
            
        user_state = self.user_states[person_id]
        if not user_state.get('last_login_time'):
            return True

        seconds_elapsed = (datetime.now() - user_state['last_login_time']).total_seconds()
        return seconds_elapsed > self.LOGIN_TIMEOUT

    def process_login(self, person_id):
        """Process login with RBAC check."""
        if self.can_login(person_id):
            # Get user's role
            role = self.get_user_role(person_id)
            if not role:
                print(f"\nUser {person_id} not found in database")
                return False

            # Check if role has access to the selected room
            has_access = self.check_access(role, self.selected_room_id)
            
            # Update user state
            self.user_states[person_id] = {
                'last_login_time': datetime.now(),
                'is_visible': True,
                'has_access': has_access,
                'role': role
            }

            # Log the access attempt
            access_status = "GRANTED" if has_access else "DENIED"
            print(f"\nAccess {access_status} for user {person_id} ({role}) to {self.selected_room}")
            return has_access

        return self.user_states[person_id].get('has_access', False)

    def draw_face_box(self, frame, location, is_authorized, person_id=None):
        """Draw a box around the face with color indicating authorization status."""
        top, right, bottom, left = location
        
        color = self.AUTHORIZED_COLOR if is_authorized else self.UNAUTHORIZED_COLOR
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw a filled rectangle for text background
        cv2.rectangle(frame, (left, bottom + 35), (right, bottom), color, cv2.FILLED)
        
        # Add text
        font = cv2.FONT_HERSHEY_DUPLEX
        if person_id and person_id in self.user_states:
            text = f"{person_id} ({self.user_states[person_id]['role']})"
        else:
            text = "Unauthorized"
        
        text_size = cv2.getTextSize(text, font, 0.6, 1)[0]
        text_x = left + (right - left - text_size[0]) // 2
        cv2.putText(frame, text, (text_x, bottom + 25), font, 0.6, (255, 255, 255), 1)

    def detect_faces(self, frame):
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(imgS)
        current_visible_users = set()

        if face_locations:
            encodeCurFrame = face_recognition.face_encodings(imgS, face_locations)
            
            original_face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                                     for top, right, bottom, left in face_locations]

            for encodeFace, face_loc in zip(encodeCurFrame, original_face_locations):
                matches = face_recognition.compare_faces(self.encodeListKnown, encodeFace)
                
                if True in matches:
                    faceDis = face_recognition.face_distance(self.encodeListKnown, encodeFace)
                    matchIndex = np.argmin(faceDis)
                    person_id = self.personIds[matchIndex]
                    current_visible_users.add(person_id)

                    has_access = self.process_login(person_id)
                    self.draw_face_box(frame, face_loc, has_access, person_id)
                else:
                    if not self.unauthorized_message_shown:
                        print("\nUnauthorized person detected")
                        self.unauthorized_message_shown = True
                    self.draw_face_box(frame, face_loc, False)

        for user_id in list(self.user_states.keys()):
            if user_id not in current_visible_users:
                if self.user_states[user_id]['is_visible']:
                    print(f"\nUser {user_id} left the frame")
                    self.user_states[user_id]['is_visible'] = False

        if not face_locations:
            self.unauthorized_message_shown = False

    def run(self):
        """Run the facial recognition system."""
        print("Starting facial recognition system...")
        print("Press 'q' to quit.")

        # Step 1: Select room
        self.select_room()

        # Step 2: Verify login credentials
        person_id = self.verify_login()
        if not person_id:
            print("Authentication failed. Exiting system.")
            return

        while True:
            success, frame = self.cap.read()
            if not success:
                print("Failed to grab frame")
                break

            self.detect_faces(frame)
            cv2.imshow("Face Login System", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nShutting down system...")
                break

        self.cleanup()

    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.conn.close()

if __name__ == "__main__":
    login_system = FacialLoginSystem()
    login_system.run()
