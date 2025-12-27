import pytest
import numpy as np
import os
from unittest.mock import MagicMock, patch, mock_open
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from face_engine import FaceEngine

@pytest.fixture
def mock_face_recognition(mocker):
    return mocker.patch('face_engine.face_recognition')

@pytest.fixture
def mock_cv2(mocker):
    return mocker.patch('face_engine.cv2')

@pytest.fixture
def face_engine(mocker):
    # Mock os.makedirs and os.path.exists
    mocker.patch('os.makedirs')
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.listdir', return_value=[])
    return FaceEngine(known_faces_dir='test_faces')

def test_initialization(mocker):
    mocker.patch('os.path.exists', return_value=False)
    mock_makedirs = mocker.patch('os.makedirs')
    mocker.patch('os.listdir', return_value=[])
    
    engine = FaceEngine(known_faces_dir='start_faces')
    
    mock_makedirs.assert_called_with('start_faces')
    assert engine.known_faces_dir == 'start_faces'

def test_reload_faces_empty(face_engine, mocker):
    mocker.patch('os.listdir', return_value=[])
    count = face_engine.reload_faces()
    assert count == 0
    assert len(face_engine.known_face_names) == 0

def test_reload_faces_with_files(face_engine, mocker, mock_face_recognition):
    # Setup mocks
    mocker.patch('os.listdir', return_value=['person_one.jpg', 'person_two.png', 'ignore.txt'])
    mocker.patch('os.path.exists', return_value=True)
    
    # Mock image loading and encoding
    mock_face_recognition.load_image_file.return_value = "fake_image_data"
    mock_face_recognition.face_encodings.side_effect = [["encoding1"], ["encoding2"]]
    
    count = face_engine.reload_faces()
    
    assert count == 2
    assert "person one" in face_engine.known_face_names
    assert "person two" in face_engine.known_face_names
    assert len(face_engine.known_face_encodings) == 2

def test_process_base64_image(face_engine, mock_cv2):
    # Mock base64 decoding
    with patch('base64.b64decode', return_value=b'binarydata'):
        mock_cv2.imdecode.return_value = "opencv_image"
        
        # Test with header
        result1 = face_engine.process_base64_image("data:image/jpeg;base64,somerandomstring")
        assert result1 == "opencv_image"
        
        # Test without header
        result2 = face_engine.process_base64_image("somerandomstring")
        assert result2 == "opencv_image"

def test_recognize_face_success(face_engine, mock_face_recognition, mock_cv2):
    # Setup known faces
    face_engine.known_face_names = ["Alice"]
    face_engine.known_face_encodings = ["alice_encoding"]
    
    # Mock detection
    mock_cv2.cvtColor.return_value = "rgb_image"
    mock_face_recognition.face_locations.return_value = ["loc1"]
    mock_face_recognition.face_encodings.return_value = ["unknown_encoding"]
    
    # Mock efficient matching
    mock_face_recognition.compare_faces.return_value = [True]
    
    status, message, name = face_engine.recognize_face("input_image")
    
    assert status == "success"
    assert name == "Alice"
    assert "dikenali" in message

def test_recognize_face_unknown(face_engine, mock_face_recognition, mock_cv2):
    # Setup known faces
    face_engine.known_face_names = ["Alice"]
    face_engine.known_face_encodings = ["alice_encoding"]
    
    # Mock detection
    mock_face_recognition.face_encodings.return_value = ["unknown_encoding"]
    
    # Mock no match
    mock_face_recognition.compare_faces.return_value = [False]
    
    status, message, name = face_engine.recognize_face("input_image")
    
    assert status == "error"
    assert name is None
    assert "tidak dikenal" in message

def test_recognize_face_no_face(face_engine, mock_face_recognition, mock_cv2):
    # Mock no face detected
    mock_face_recognition.face_encodings.return_value = []
    
    status, message, _ = face_engine.recognize_face("input_image")
    
    assert status == "error"
    assert "tidak terdeteksi" in message

def test_register_face_success(face_engine, mocker):
    mocker.patch('builtins.open', mock_open())
    mock_reload = mocker.patch.object(face_engine, 'reload_faces')
    
    success, msg = face_engine.register_face("New User", "dGVzdA==")
    
    assert success is True
    assert "berhasil didaftarkan" in msg
    mock_reload.assert_called_once()
