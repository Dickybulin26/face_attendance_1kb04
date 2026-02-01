import face_recognition
import cv2
import numpy as np
import base64
import os

class FaceEngine:
    def __init__(self, known_faces_dir='known_faces'):
        self.known_faces_dir = known_faces_dir
        self.known_encodings = []
        self.known_names = []
        # Load known faces on initialization
        self.load_known_faces()

    def load_known_faces(self):
        """Reload face database from folder to memory"""
        self.known_encodings = []
        self.known_names = []
        
        # Create folder if it doesn't exist
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
            
        print("Loading face database...")
        
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(self.known_faces_dir, filename)
                try:
                    image = face_recognition.load_image_file(path)
                    encoding = face_recognition.face_encodings(image)
                    if encoding:
                        self.known_encodings.append(encoding[0])
                        self.known_names.append(os.path.splitext(filename)[0])
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        
        print(f"Database ready! Total users: {len(self.known_names)}")

    def process_base64_image(self, base64_string):
        """Convert base64 string from webcam to OpenCV image"""
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Image optimization: Brighten slightly for easier detection
        img = cv2.convertScaleAbs(img, alpha=1.1, beta=10)
        
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def recognize_face(self, rgb_img):
        """Attendance Process (Scan)"""
        # Upsample 1x is sufficient for fast scanning
        face_locations = face_recognition.face_locations(rgb_img)
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

        if not face_encodings:
            return "error", "Face not detected", None

        for face_encoding in face_encodings:
            # Tolerance 0.5 for accuracy
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    nama = self.known_names[best_match_index]
                    return "success", "Face recognized", nama

        return "error", "Face not recognized", None

    def register_face(self, nama, base64_image):
        """New Face Registration Process (More Precise)"""
        try:
            img_rgb = self.process_base64_image(base64_image)
            
            # --- ANTI-FAILURE DETECTION FEATURE ---
            # number_of_times_to_upsample=1 is balance between speed & accuracy
            face_locations = face_recognition.face_locations(img_rgb, number_of_times_to_upsample=1)
            
            if not face_locations:
                # Try again with high contrast if failed
                img_enhanced = cv2.convertScaleAbs(img_rgb, alpha=1.5, beta=20)
                face_locations = face_recognition.face_locations(img_enhanced, number_of_times_to_upsample=1)
                
                if not face_locations:
                    return False, "Face not found. Try moving closer to the camera."

            # --- VALIDATION: ONLY 1 FACE ALLOWED ---
            if len(face_locations) > 1:
                return False, "Only 1 face is allowed per image!"

            # Get encoding
            face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
            
            if not face_encodings:
                return False, "Face detected but blurry. Ensure sufficient lighting."

            # Save file
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            file_path = os.path.join(self.known_faces_dir, f"{nama}.jpg")
            cv2.imwrite(file_path, img_bgr)
            
            # --- OPTIMIZATION: APPEND TO MEMORY WITHOUT FULL RELOAD ---
            self.known_encodings.append(face_encodings[0])
            self.known_names.append(nama)
            
            return True, f"Success! Face {nama} saved."

        except Exception as e:
            print(f"Error Register: {str(e)}")
            return False, f"System Error: {str(e)}"