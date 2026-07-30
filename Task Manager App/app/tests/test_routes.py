def test_login_page_loads(client):
    response = client.get('/auth/login')
    assert response.status_code == 200

from app.models import User
from app import db
from werkzeug.security import generate_password_hash

def test_login_with_valid_credentials(client):
    from app import create_app  # or however your app factory is imported
    
    with client.application.app_context():
        user = User(username='testuser', email='test@example.com',
                    password=generate_password_hash('testpass123'))
        db.session.add(user)
        db.session.commit()

    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'testpass123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome back' in response.data

def test_add_task_requires_login(client):
    response = client.get('/tasks/add')
    assert response.status_code == 302  # redirect, not 200