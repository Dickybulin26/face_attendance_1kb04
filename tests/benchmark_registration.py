import time
import os
import sys
import numpy as np
import cv2
import base64

# Add current dir to path to import local modules
sys.path.append(os.getcwd())
from face_engine import FaceEngine

def test_performance():
    engine = FaceEngine()
    
    # Create a dummy white image with a simulated face (using a real image would be better but for timing we can use one from known_faces)
    known_faces = [f for f in os.listdir('known_faces') if f.endswith('.jpg')]
    if not known_faces:
        print("No faces found in known_faces for testing.")
        return
        
    test_image_path = os.path.join('known_faces', known_faces[0])
    with open(test_image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        base64_image = f"data:image/jpeg;base64,{encoded_string}"

    print(f"--- Testing registration speed with {test_image_path} ---")
    
    start_time = time.time()
    success, message = engine.register_face("TestLatency", base64_image)
    end_time = time.time()
    
    print(f"Success: {success}")
    print(f"Message: {message}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    
    # Cleanup
    if os.path.exists('known_faces/TestLatency.jpg'):
        os.remove('known_faces/TestLatency.jpg')

if __name__ == "__main__":
    test_performance()
