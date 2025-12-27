import face_recognition
import cv2
import numpy as np
import os
import base64


class FaceEngine:
    def __init__(self, known_faces_dir='known_faces'):
        """
        Initialize the FaceEngine object.

        Parameters
        ----------
        known_faces_dir : str, optional
            The directory where known faces are stored, by default 'known_faces'.
        """

        self.known_faces_dir = known_faces_dir
        self.known_face_encodings = []
        self.known_face_names = []

        # Ensure directory exists
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)

        self.reload_faces()

    def reload_faces(self):
        """
        Reload all known faces from the directory.

        Returns
        -------
        int
            The number of known faces loaded.
        """
        self.known_face_encodings = []
        self.known_face_names = []

        if not os.path.exists(self.known_faces_dir):
            return 0

        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                path = os.path.join(self.known_faces_dir, filename)
                try:
                    img = face_recognition.load_image_file(path)
                    enc = face_recognition.face_encodings(img)
                    if enc:
                        self.known_face_encodings.append(enc[0])
                        # Format nama agar rapi saat disebut TTS (ganti underscore ke spasi)
                        clean_name = os.path.splitext(
                            filename)[0].replace("_", " ")
                        self.known_face_names.append(clean_name)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

        print(f"🔄 Database wajah dimuat: {len(self.known_face_names)} orang.")
        return len(self.known_face_names)

    def process_base64_image(self, base64_string):
        """
        Process a base64 encoded image string.

        Parameters
        ----------
        base64_string : str
            The base64 encoded image string.

        Returns
        -------
        img : numpy.ndarray
            The decoded image as a numpy array, or None if there is an error.
        """
        try:
            if "," in base64_string:
                _, encoded = base64_string.split(",", 1)
            else:
                encoded = base64_string

            nparr = np.frombuffer(base64.b64decode(encoded), np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            print(f"Error processing base64 image: {e}")
            return None

    def recognize_face(self, img, tolerance=0.5):
        """
        Recognize a face in an image.

        Parameters
        ----------
        img : numpy.ndarray
            The image to recognize, as a numpy array.
        tolerance : float, optional
            The tolerance for face recognition, by default 0.5.

        Returns
        -------
        status : str
            The status of the recognition, can be "success", "error", or None.
        message : str
            A message indicating the result of the recognition.
        name : str or None
            The name of the recognized face, or None if not recognized.
        """
        if img is None:
            return "error", "Gagal memproses gambar.", None

        # Konversi ke RGB untuk face_recognition
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Deteksi Wajah
        face_locations = face_recognition.face_locations(rgb_img)
        encs = face_recognition.face_encodings(rgb_img, face_locations)

        if not encs:
            return "error", "Wajah tidak terdeteksi!", None

        # Komparasi Wajah (Check against all known faces)
        # We only check the first face detected for attendance
        matches = face_recognition.compare_faces(
            self.known_face_encodings, encs[0], tolerance=tolerance)

        if True in matches:
            first_match_index = matches.index(True)
            name = self.known_face_names[first_match_index]
            return "success", f"Wajah dikenali: {name}", name

        return "error", "Wajah tidak dikenal.", None

    def register_face(self, name, base64_image):
        """
        Register a face with the given name and base64 image.

        Parameters
        ----------
        name : str
            The name of the face to register.
        base64_image : str
            The base64 encoded image of the face to register.

        Returns
        -------
        bool
            True if the face is successfully registered, False otherwise.
        str
            A message indicating the result of the registration.
        """
        try:
            filename = name.lower().replace(" ", "_")
            filepath = os.path.join(self.known_faces_dir, f"{filename}.jpg")

            if "," in base64_image:
                data = base64_image.split(",", 1)[1]
            else:
                data = base64_image

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(data))

            self.reload_faces()
            return True, f"Wajah {filename} berhasil didaftarkan!"
        except Exception as e:
            return False, f"Gagal menyimpan wajah: {str(e)}"
