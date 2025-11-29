from datetime import datetime
from backend.app import db
from backend.utils.timezone import get_utc_now, format_ist_iso

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_available_spots_count(self):
        """Get count of available parking spots"""
        return self.parking_spots.filter_by(status='A').count()
    
    def get_occupied_spots_count(self):
        """Get count of occupied parking spots"""
        return self.parking_spots.filter_by(status='O').count()
    
    def to_dict(self):
        """Convert parking lot object to dictionary"""
        return {
            'id': self.id,
            'prime_location_name': self.prime_location_name,
            'address': self.address,
            'pin_code': self.pin_code,
            'price_per_hour': self.price_per_hour,
            'number_of_spots': self.number_of_spots,
            'available_spots': self.get_available_spots_count(),
            'occupied_spots': self.get_occupied_spots_count(),
            'description': self.description,
            'created_at': format_ist_iso(self.created_at),
            'updated_at': format_ist_iso(self.updated_at),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'

