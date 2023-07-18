from flask_login import UserMixin, login_manager
from prisma.models import User

def get_user(email):
    user = User.prisma().find_first(where={'email': email})
    return user
class UserModel(UserMixin):
    def __init__(self, user):
        self.id = user.id
        self.email = user.email
        self.password = user.password
        self.name = user.name
        self.active = user.active
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.email)
    @property
    def is_active(self):
        return self.active
    @property
    def is_authenticated(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.id
    @staticmethod
    def get(user_id):
        user = User.prisma().find_first(where={'id': user_id})
        if user is not None:
            return UserModel(user)
        return None