import pytest
from app import create_app, db

@pytest.fixture
def client():
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
    }
    app = create_app(test_config=test_config)

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client