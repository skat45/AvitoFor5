from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from app import app

app.secret_key = 'iu413bstopchtozakluchnadonormalniy'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///avito_data_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String())
    password_hash = db.Column(db.String())
    room = db.Column(db.Integer)
    vk = db.Column(db.String(50), nullable=True)
    tg = db.Column(db.String(50), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def add(user_login, user_password_hash, user_room):
        db.session.add(User(login=user_login, password_hash=user_password_hash, room=user_room))
        db.session.commit()


class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String())
    cost = db.Column(db.String(50))
    image = db.Column(db.String(60), nullable=True)
    owner_id = db.Column(db.Integer)

    def add(name, desc, lacost, image_name, o_id):
        db.session.add(Advertisement(title=name, description=desc, cost=lacost, image=image_name, owner_id=o_id))
        db.session.commit()
