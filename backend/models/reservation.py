from datetime import datetime
from backend.app import db
from backend.utils.timezone import get_utc_now, format_ist_iso

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    vehicle_number = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(50), default='4-Wheeler')
    parking_timestamp = db.Column(db.DateTime, default=get_utc_now, nullable=False)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # 'pending', 'paid', 'cancelled'
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'cancelled'
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_utc_now)
    
    def calculate_cost(self, price_per_hour):
        """Calculate parking cost based on duration"""
        if self.leaving_timestamp:
            duration = (self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600
            self.parking_cost = round(duration * price_per_hour, 2)
        return self.parking_cost
    
    def get_duration_hours(self):
        """Get duration in hours"""
        if self.leaving_timestamp:
            return round((self.leaving_timestamp - self.parking_timestamp).total_seconds() / 3600, 2)
        elif self.status == 'active':
            return round((get_utc_now() - self.parking_timestamp).total_seconds() / 3600, 2)
        return 0
    
    def to_dict(self):
        """Convert reservation object to dictionary"""
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'vehicle_number': self.vehicle_number,
            'vehicle_type': self.vehicle_type,
            'parking_timestamp': format_ist_iso(self.parking_timestamp),
            'leaving_timestamp': format_ist_iso(self.leaving_timestamp),
            'parking_cost': self.parking_cost,
            'payment_status': self.payment_status,
            'status': self.status,
            'remarks': self.remarks,
            'duration_hours': self.get_duration_hours(),
            'created_at': format_ist_iso(self.created_at)
        }
    
    def __repr__(self):
        return f'<Reservation {self.id} - User {self.user_id}>'

