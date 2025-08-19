from app.models.user import User
from app import db

def get_all_users():
    return User.query.all()

def find_user_by_id(user_id):
    return User.query.get(user_id)

def update_user(user_id, data):
    if 'username' in data:
        user = find_user_by_id(user_id)
        if user:
            user.username = data['username']
        else:
            return None
    if 'email' in data:
        user = find_user_by_id(user_id)
        if user:
            user.email = data['email']
        else:
            return None
    db.session.commit()
    return user