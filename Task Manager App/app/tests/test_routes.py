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


def test_add_task_empty_title_fails(client):
    from app.models import User
    from app import db
    from werkzeug.security import generate_password_hash

    with client.application.app_context():
        user = User(username='formtest', email='formtest@example.com',
                    password=generate_password_hash('pass123'))
        db.session.add(user)
        db.session.commit()

    # Log in first, since /tasks/add requires authentication
    client.post('/auth/login', data={
        'email': 'formtest@example.com',
        'password': 'pass123'
    }, follow_redirects=True)

    # Now try submitting an empty title
    response = client.post('/tasks/add', data={
        'title': '',
        'description': 'test',
        'priority': 'medium'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'This field is required' in response.data


import json

def test_jwt_login_and_protected_route(client):
    from app.models import User
    from app import db
    from werkzeug.security import generate_password_hash

    with client.application.app_context():
        user = User(username='jwtuser', email='jwt@example.com',
                    password=generate_password_hash('jwtpass123'))
        db.session.add(user)
        db.session.commit()

    # Step 1: Login via JWT endpoint
    login_response = client.post('/api/login', 
        json={'email': 'jwt@example.com', 'password': 'jwtpass123'})
    
    assert login_response.status_code == 200
    token = login_response.get_json()['token']
    assert token is not None

    # Step 2: Use the token to hit a protected route
    protected_response = client.get('/api/tasks',
        headers={'Authorization': f'Bearer {token}'})
    
    assert protected_response.status_code == 200

    
    
def test_edit_task_success(client):
    from app.models import User, Task, Category
    from app import db
    from werkzeug.security import generate_password_hash

    with client.application.app_context():
        user = User(username='edituser', email='edit@example.com',
                    password=generate_password_hash('editpass'))
        db.session.add(user)
        db.session.commit()

        task = Task(title='Original Title', description='old desc',
                    priority='low', user_id=user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id  # save the id before the session context closes

    # Log in
    client.post('/auth/login', data={
        'email': 'edit@example.com',
        'password': 'editpass'
    }, follow_redirects=True)

    # Edit the task
    response = client.post(f'/tasks/edit/{task_id}', data={
        'title': 'Updated Title',
        'description': 'new desc',
        'priority': 'high',
        'category_id': '0'
    }, follow_redirects=True)

    assert response.status_code == 200

    # Confirm the actual database side effect
    with client.application.app_context():
        updated_task = Task.query.get(task_id)
        assert updated_task.title == 'Updated Title'
        assert updated_task.priority == 'high'



def test_edit_task_wrong_user_blocked(client):
    from app.models import User, Task
    from app import db
    from werkzeug.security import generate_password_hash

    with client.application.app_context():
        # User A owns the task
        user_a = User(username='usera', email='usera@example.com',
                      password=generate_password_hash('passA'))
        db.session.add(user_a)
        db.session.commit()

        task = Task(title='User A Task', priority='low', user_id=user_a.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # User B is a different, unrelated user
        user_b = User(username='userb', email='userb@example.com',
                      password=generate_password_hash('passB'))
        db.session.add(user_b)
        db.session.commit()

    # Log in as User B, NOT User A
    client.post('/auth/login', data={
        'email': 'userb@example.com',
        'password': 'passB'
    }, follow_redirects=True)

    # User B tries to edit User A's task
    response = client.get(f'/tasks/edit/{task_id}')

    assert response.status_code == 404