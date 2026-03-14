from datetime import datetime
from extensions import db


class Contact(db.Model):
    __tablename__ = 'contacts'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False, index=True)
    street      = db.Column(db.String(300))
    city        = db.Column(db.String(100), index=True)
    state       = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country     = db.Column(db.String(100), index=True)
    phone       = db.Column(db.String(50), unique=True)
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
