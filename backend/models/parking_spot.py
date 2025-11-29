from datetime import datetime
from backend.app import db
from backend.utils.timezone import get_utc_now, format_ist_iso

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False, index=True)
    spot_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(1), default='A')  # 'A' = Available, 'O' = Occupied
    floor_number = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert parking spot object to dictionary"""
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'spot_number': self.spot_number,
            'status': self.status,
            'status_text': 'Available' if self.status == 'A' else 'Occupied',
            'floor_number': self.floor_number,
            'created_at': format_ist_iso(self.created_at)
        }
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} - {self.status}>'

