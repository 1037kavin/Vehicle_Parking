from datetime import datetime, timedelta
from flask_mail import Message
from backend.tasks.celery_config import celery
from backend.app import create_app, db, mail
from backend.models import User, Reservation
from backend.utils.timezone import get_ist_now

@celery.task(name='backend.tasks.daily_reminder.send_daily_reminders')
def send_daily_reminders():
    """Send daily reminders to inactive users"""
    app = create_app()
    
    with app.app_context():
        # Get users who haven't made any reservations in the last 7 days
        seven_days_ago = get_ist_now() - timedelta(days=7)
        
        # Find inactive users
        all_users = User.query.filter_by(role='user', is_active=True).all()
        inactive_users = []
        
        for user in all_users:
            recent_reservation = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.created_at >= seven_days_ago
            ).first()
            
            if not recent_reservation:
                inactive_users.append(user)
        
        # Send email reminders
        reminders_sent = 0
        for user in inactive_users:
            try:
                msg = Message(
                    subject='🚗 Parking Reminder - Need a Spot Today?',
                    recipients=[user.email],
                    body=f"""Hi {user.full_name or user.username},

We noticed you haven't booked a parking spot in the last 7 days.

Planning to visit today? Don't forget to book your parking spot in advance!

📱 Quick Actions:
- Book a parking spot now
- Check available parking lots
- View your parking history

Best regards,
Parking Manager Team

---
This is an automated reminder. If you don't need parking, you can ignore this message.
"""
                )
                mail.send(msg)
                reminders_sent += 1
                print(f"Reminder sent to {user.email}")
            except Exception as e:
                print(f"Failed to send reminder to {user.email}: {str(e)}")
        
        return f"Daily reminders sent to {reminders_sent} out of {len(inactive_users)} inactive users"

