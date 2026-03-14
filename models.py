from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    contacts      = db.relationship('Contact', backref='owner', lazy='dynamic',
                                    cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Contact(db.Model):
    __tablename__ = 'contacts'
    __table_args__ = (
        # Phone unique per user — different users may share the same number
        db.UniqueConstraint('user_id', 'phone', name='uq_contact_user_phone'),
    )

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name        = db.Column(db.String(200), nullable=False, index=True)
    street      = db.Column(db.String(300))
    city        = db.Column(db.String(100), index=True)
    state       = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country     = db.Column(db.String(100), index=True)
    phone       = db.Column(db.String(50))
    email       = db.Column(db.String(150), index=True)
    latitude    = db.Column(db.Float)
    longitude   = db.Column(db.Float)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def display_address(self):
        parts = [p for p in [self.street, self.city, self.state,
                              self.postal_code, self.country] if p]
        return ', '.join(parts)

    def __repr__(self):
        return f'<Contact {self.name}>'
