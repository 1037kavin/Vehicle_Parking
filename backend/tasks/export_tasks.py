import csv
import os
from datetime import datetime
from flask_mail import Message
from backend.tasks.celery_config import celery
from backend.app import create_app, db, mail
from backend.models import Reservation, ParkingSpot, ParkingLot

@celery.task(name='backend.tasks.export_tasks.export_user_reservations_csv')
def export_user_reservations_csv(user_id, user_email):
    """Export user reservations to CSV and send via email"""
    app = create_app()
    
    with app.app_context():
        # Get all reservations
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
        
        # Create CSV file
        filename = f'parking_history_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        filepath = os.path.join('/tmp', filename)
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Reservation ID', 'Parking Lot', 'Spot Number', 'Vehicle Number',
                'Parking Timestamp', 'Leaving Timestamp', 'Duration (hours)',
                'Parking Cost', 'Payment Status', 'Status', 'Remarks'
            ])
            
            # Write data
            for res in reservations:
                spot = ParkingSpot.query.get(res.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                
                writer.writerow([
                    res.id,
                    lot.prime_location_name,
                    spot.spot_number,
                    res.vehicle_number,
                    res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.parking_timestamp else '',
                    res.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.leaving_timestamp else 'Active',
                    res.get_duration_hours(),
                    res.parking_cost,
                    res.payment_status,
                    res.status,
                    res.remarks or ''
                ])
        
        # Send email with attachment
        try:
            msg = Message(
                subject='Your Parking History Export',
                recipients=[user_email],
                body='Please find attached your parking history export.'
            )
            
            with open(filepath, 'rb') as fp:
                msg.attach(filename, 'text/csv', fp.read())
            
            mail.send(msg)
            print(f"CSV export sent to {user_email}")
            
            # Clean up file
            os.remove(filepath)
            
            return f"CSV export sent to {user_email}"
        
        except Exception as e:
            print(f"Failed to send CSV export: {str(e)}")
            raise

