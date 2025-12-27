import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret'
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_mongo(mocker):
    mock_client = mocker.patch('app.MongoClient')
    mock_db = MagicMock()
    mock_client.return_value = {'db_absensi': mock_db}
    return mock_db

@pytest.fixture
def mock_face_engine(mocker):
    return mocker.patch('app.face_engine')

def test_index_redirect(client):
    """Test user is redirected to login if not authenticated"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_login_page_load(client):
    """Test login page loads correctly"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_success(client):
    """Test valid login credentials"""
    response = client.post('/login', data={
        'username': 'admin',
        'password': '123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should be on index page now
    with client.session_transaction() as sess:
        assert sess['user'] == 'admin'
        assert sess['role'] == 'admin'

def test_login_fail(client):
    """Test invalid login credentials"""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    
    assert b'Login Gagal' in response.data

def test_api_process_image_success(client, mock_face_engine, mock_mongo, mocker):
    # Mock Mongo
    mock_collection = MagicMock()
    mock_mongo.__getitem__.return_value = mock_collection
    # Mock find_one to return None (not already present)
    mocker.patch('app.collection.find_one', return_value=None)
    mocker.patch('app.collection.insert_one')
    
    # Mock FaceEngine
    mock_face_engine.process_base64_image.return_value = "fake_img"
    mock_face_engine.recognize_face.return_value = ("success", "Wajah dikenali: TestUser", "TestUser")
    
    response = client.post('/process_image', json={'image': 'fake_base64_data'})
    
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert json_data['nama'] == 'TestUser'

def test_api_process_image_unknown(client, mock_face_engine):
    # Mock FaceEngine to return error (unknown face)
    mock_face_engine.process_base64_image.return_value = "fake_img"
    mock_face_engine.recognize_face.return_value = ("error", "Wajah tidak dikenal.", None)
    
    response = client.post('/process_image', json={'image': 'fake_base64_data'})
    
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert 'tidak dikenal' in json_data['message']

def test_api_process_image_duplicate(client, mock_face_engine, mocker):
    # Mock Mongo to return existing log
    mocker.patch('app.collection.find_one', return_value={"nama": "TestUser", "tanggal": "2024-01-01"})
    
    # Mock FaceEngine
    mock_face_engine.process_base64_image.return_value = "fake_img"
    mock_face_engine.recognize_face.return_value = ("success", "Wajah dikenali", "TestUser")
    
    response = client.post('/process_image', json={'image': 'fake_base64_data'})
    
    json_data = response.get_json()
    assert json_data['status'] == 'already_present'
    assert 'sudah terabsensi' in json_data['message']
