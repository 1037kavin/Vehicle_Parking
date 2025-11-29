from datetime import datetime, timedelta
from flask_mail import Message
from sqlalchemy import func
import csv
import io
from backend.tasks.celery_config import celery
from backend.app import create_app, db, mail
from backend.models import User, Reservation, ParkingSpot, ParkingLot

@celery.task(name='backend.tasks.monthly_report.generate_monthly_reports')
def generate_monthly_reports():
    """Generate and send monthly activity reports to all users"""
    app = create_app()
    
    with app.app_context():
        # Get all active users
        users = User.query.filter_by(role='user', is_active=True).all()
        
        # Get last month's date range
        today = datetime.utcnow()
        first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        month_name = last_day_previous_month.strftime('%B %Y')
        
        reports_sent = 0
        
        for user in users:
            # Get user's reservations for last month
            reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= first_day_previous_month,
                Reservation.created_at < first_day_current_month
            ).all()
            
            if not reservations:
                continue  # Skip users with no activity
            
            # Calculate statistics
            total_bookings = len(reservations)
            total_spent = sum([r.parking_cost for r in reservations if r.parking_cost])
            
            # Most used parking lot
            lot_usage = db.session.query(
                ParkingLot.prime_location_name,
                func.count(Reservation.id).label('count')
            ).join(
                ParkingSpot, ParkingSpot.lot_id == ParkingLot.id
            ).join(
                Reservation, Reservation.spot_id == ParkingSpot.id
            ).filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= first_day_previous_month,
                Reservation.created_at < first_day_current_month
            ).group_by(
                ParkingLot.id
            ).order_by(
                func.count(Reservation.id).desc()
            ).first()
            
            most_used_lot = lot_usage[0] if lot_usage else 'N/A'
            
            # Generate CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Date', 'Parking Lot', 'Spot', 'Vehicle Number', 'Check In', 'Check Out', 'Duration (hrs)', 'Cost (₹)', 'Payment Status', 'Status'])
            
            for res in reservations:
                spot = ParkingSpot.query.get(res.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                writer.writerow([
                    res.created_at.strftime('%Y-%m-%d') if res.created_at else 'N/A',
                    lot.prime_location_name,
                    spot.spot_number,
                    res.vehicle_number,
                    res.parking_timestamp.strftime('%Y-%m-%d %H:%M') if res.parking_timestamp else 'N/A',
                    res.leaving_timestamp.strftime('%Y-%m-%d %H:%M') if res.leaving_timestamp else 'Active',
                    res.get_duration_hours(),
                    res.parking_cost or 0,
                    res.payment_status,
                    res.status
                ])
            
            # Send email with CSV attachment
            try:
                msg = Message(
                    subject=f'Your Monthly Parking Report - {month_name}',
                    recipients=[user.email],
                    body=f"""Hi {user.full_name or user.username},

Your parking activity summary for {month_name}:

📊 Statistics:
- Total Bookings: {total_bookings}
- Total Spent: ₹{total_spent:.2f}
- Most Used Parking Lot: {most_used_lot}

Please find your detailed activity report in the attached CSV file.

Thank you for using Parking Manager!

Best regards,
Parking App Team
"""
                )
                
                # Attach CSV file
                msg.attach(
                    f"parking_report_{month_name.replace(' ', '_')}.csv",
                    "text/csv",
                    output.getvalue()
                )
                
                mail.send(msg)
                reports_sent += 1
                print(f"Report sent to {user.email}")
            except Exception as e:
                print(f"Failed to send report to {user.email}: {str(e)}")
        
        return f"Monthly reports sent to {reports_sent} users"

@celery.task(name='backend.tasks.monthly_report.generate_monthly_reports_test')
def generate_monthly_reports_test():
    """Generate and send monthly reports for CURRENT MONTH (for testing)"""
    app = create_app()
    
    with app.app_context():
        # Get all active users
        users = User.query.filter_by(role='user', is_active=True).all()
        
        # Get CURRENT month's date range (for testing)
        today = datetime.utcnow()
        first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        month_name = today.strftime('%B %Y')
        
        reports_sent = 0
        
        for user in users:
            # Get user's reservations for CURRENT month
            reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= first_day_current_month
            ).all()
            
            if not reservations:
                print(f"No reservations for {user.username} in current month")
                continue  # Skip users with no activity
            
            # Calculate statistics
            total_bookings = len(reservations)
            total_spent = sum([r.parking_cost for r in reservations if r.parking_cost])
            
            # Most used parking lot
            lot_usage = db.session.query(
                ParkingLot.prime_location_name,
                func.count(Reservation.id).label('count')
            ).join(
                ParkingSpot, ParkingSpot.lot_id == ParkingLot.id
            ).join(
                Reservation, Reservation.spot_id == ParkingSpot.id
            ).filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= first_day_current_month
            ).group_by(
                ParkingLot.id
            ).order_by(
                func.count(Reservation.id).desc()
            ).first()
            
            most_used_lot = lot_usage[0] if lot_usage else 'N/A'
            
            # Generate CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Date', 'Parking Lot', 'Spot', 'Vehicle Number', 'Check In', 'Check Out', 'Duration (hrs)', 'Cost (₹)', 'Payment Status', 'Status'])
            
            for res in reservations:
                spot = ParkingSpot.query.get(res.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                writer.writerow([
                    res.created_at.strftime('%Y-%m-%d') if res.created_at else 'N/A',
                    lot.prime_location_name,
                    spot.spot_number,
                    res.vehicle_number,
                    res.parking_timestamp.strftime('%Y-%m-%d %H:%M') if res.parking_timestamp else 'N/A',
                    res.leaving_timestamp.strftime('%Y-%m-%d %H:%M') if res.leaving_timestamp else 'Active',
                    res.get_duration_hours(),
                    res.parking_cost or 0,
                    res.payment_status,
                    res.status
                ])
            
            # Send email with CSV attachment
            try:
                msg = Message(
                    subject=f'🧪 TEST - Your Parking Report - {month_name}',
                    recipients=[user.email],
                    body=f"""Hi {user.full_name or user.username},

🧪 This is a TEST monthly report for {month_name} (current month).

📊 Statistics:
- Total Bookings: {total_bookings}
- Total Spent: ₹{total_spent:.2f}
- Most Used Parking Lot: {most_used_lot}

Please find your detailed activity report in the attached CSV file.

Thank you for using Parking Manager!

Best regards,
Parking App Team

---
Note: This is a test report. In production, reports are sent on the 1st of each month for the previous month's activity.
"""
                )
                
                # Attach CSV file
                msg.attach(
                    f"parking_report_{month_name.replace(' ', '_')}_TEST.csv",
                    "text/csv",
                    output.getvalue()
                )
                
                mail.send(msg)
                reports_sent += 1
                print(f"Test report sent to {user.email}")
            except Exception as e:
                print(f"Failed to send test report to {user.email}: {str(e)}")
        
        return f"TEST: Monthly reports sent to {reports_sent} users for current month ({month_name})"

