from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, faculty, student
    is_representative = db.Column(db.Boolean, default=False)  # For student representatives
    is_active = db.Column(db.Boolean, default=True)  # Account status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with bookings
    bookings = db.relationship('Booking', backref='user', lazy=True, foreign_keys='Booking.user_id')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # seminar_hall, lab, auditorium, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with bookings
    bookings = db.relationship('Booking', backref='venue', lazy=True)
    
    def __repr__(self):
        return f'<Venue {self.name}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)  # e.g., "09:00-10:00"
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected, Cancelled
    document_path = db.Column(db.String(255))  # Path to uploaded permission document
    override_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Who overrode this booking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship for override_by
    override_user = db.relationship('User', foreign_keys=[override_by], backref='overridden_bookings')
    
    def __repr__(self):
        return f'<Booking {self.id} - {self.venue.name} on {self.date}>'
