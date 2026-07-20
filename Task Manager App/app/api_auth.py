from flask import Blueprint,request,jsonify
from app.models import User
import jwt
from datetime import datetime, timedelta
from flask import current_app 
from werkzeug.security import check_password_hash

api_auth = Blueprint('api_auth',__name__)



@api_auth.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, current_app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401


from app.decorators import token_required
from app.models import Task

@api_auth.route('/api/tasks', methods=['GET'])
@token_required
def api_get_tasks(current_user_id):
    tasks = Task.query.filter_by(user_id=current_user_id).all()
    return jsonify([{'id': t.id, 'title': t.title, 'priority': t.priority} for t in tasks])

