import pytest
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db
from app.models.user import User, UserRole
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        db.drop_all()
        
def test_create_user(client):
    response = client.post('/user', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert 'User created successfully' in response.get_json()['message']
    
def test_admin_route_access(client):
    # Create an admin user
    client.post('/register', json={
        'username': 'adminuser',
        'email': 'admin@example.com',
        'password': 'adminpassword',
        'role': 'admin'
    })
    
    # Log in as admin to get JWT
    response = client.post('/login', json={
        'username': 'adminuser',
        'password': 'adminpassword'
    })
    access_token = response.get_json()['access_token']
    
    # Access admin route
    response = client.get('/admin', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    
def test_user_route_access_denied(client):
    # Create a regular user
    client.post('/register', json={
        'username': 'regularuser',
        'email': 'user@example.com',
        'password': 'userpassword',
        'role': 'user'
    })

    # Log in as regular user to get JWT
    response = client.post('/login', json={
        'username': 'regularuser',
        'password': 'userpassword'
    })
    access_token = response.get_json()['access_token']

    # Attempt to access admin route
    response = client.get('/admin', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 403

class UserRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            
    def test_login_success(self):
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        response = self.client.post('/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

    def test_login_failure(self):
        response = self.client.post('/login', json={
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid username or password', response.get_json()['message'])

if __name__ == '__main__':
    unittest.main()
