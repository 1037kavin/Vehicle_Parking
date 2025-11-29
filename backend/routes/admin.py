from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.app import db, mail
from backend.models import User, ParkingLot, ParkingSpot, Reservation
from backend.utils.timezone import get_ist_now, format_ist_iso

admin_bp = Blueprint('admin', __name__)

def is_admin():
    """Check if current user is admin"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return user and user.role == 'admin'

@admin_bp.route('/dashboard-stats', methods=['GET'])
@admin_bp.route('/dashboard-stats/', methods=['GET'])
@admin_bp.route('/dashboard', methods=['GET'])
@admin_bp.route('/dashboard/', methods=['GET'])
@jwt_required()
def get_admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get statistics
        total_users = User.query.filter_by(role='user').count()
        total_parking_lots = ParkingLot.query.count()
        total_spots = ParkingSpot.query.count()
        available_spots = ParkingSpot.query.filter_by(status='A').count()
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        
        active_reservations = Reservation.query.filter_by(status='active').count()
        total_reservations = Reservation.query.count()
        completed_reservations = Reservation.query.filter_by(status='completed').count()
        
        # Revenue statistics
        total_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.status == 'completed'
        ).scalar() or 0
        
        # Calculate today's revenue
        today_start = get_ist_now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.leaving_timestamp >= today_start,
            Reservation.status == 'completed'
        ).scalar() or 0
        
        # Get parking lot data for charts
        lots = ParkingLot.query.all()
        lot_names = [lot.prime_location_name for lot in lots]
        lot_spot_counts = [lot.number_of_spots for lot in lots]
        
        # Recent activities
        recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
        recent_activities = []
        for res in recent_reservations:
            user = User.query.get(res.user_id)
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            recent_activities.append({
                'id': res.id,
                'user_name': user.full_name or user.username,
                'lot_name': lot.prime_location_name,
                'spot_number': spot.spot_number,
                'parking_timestamp': format_ist_iso(res.parking_timestamp) if res.parking_timestamp else None,
                'leaving_timestamp': format_ist_iso(res.leaving_timestamp) if res.leaving_timestamp else None,
                'status': res.status,
                'parking_cost': res.parking_cost or 0
            })
        
        return jsonify({
            'total_parking_lots': total_parking_lots,
            'total_parking_spots': total_spots,
            'available_spots': available_spots,
            'occupied_spots': occupied_spots,
            'total_users': total_users,
            'active_reservations': active_reservations,
            'today_revenue': round(today_revenue, 2),
            'total_revenue': round(total_revenue, 2),
            'lot_names': lot_names,
            'lot_spot_counts': lot_spot_counts
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_bp.route('/users/', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all registered users"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        users = User.query.filter_by(role='user').all()
        user_list = []
        for user in users:
            user_dict = user.to_dict()
            # Count active reservations
            active_reservations = Reservation.query.filter_by(
                user_id=user.id, 
                status='active'
            ).count()
            user_dict['active_reservations'] = active_reservations
            user_list.append(user_dict)
        
        return jsonify(user_list), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_details(user_id):
    """Get detailed information about a specific user"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's reservation history
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        reservation_list = []
        for res in reservations:
            res_dict = res.to_dict()
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            res_dict['spot'] = spot.to_dict()
            res_dict['lot'] = lot.to_dict()
            reservation_list.append(res_dict)
        
        return jsonify({
            'user': user.to_dict(),
            'reservations': reservation_list,
            'total_reservations': len(reservations),
            'active_reservations': len([r for r in reservations if r.status == 'active'])
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    """Activate or deactivate a user"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'admin':
            return jsonify({'error': 'Cannot deactivate admin user'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'message': f"User {'activated' if user.is_active else 'deactivated'} successfully",
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user (only if they have no active reservations)"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Don't allow deleting admin users
        if user.role == 'admin':
            return jsonify({'error': 'Cannot delete admin users'}), 403
        
        # Check for active reservations
        active_reservations = Reservation.query.filter_by(
            user_id=user_id,
            status='active'
        ).count()
        
        if active_reservations > 0:
            return jsonify({
                'error': f'Cannot delete user with {active_reservations} active reservation(s). Please ask them to check out first.'
            }), 400
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reservations', methods=['GET'])
@admin_bp.route('/reservations/', methods=['GET'])
@jwt_required()
def get_all_reservations():
    """Get all reservations"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        status = request.args.get('status')
        lot_id = request.args.get('lot_id', type=int)
        
        query = Reservation.query
        
        if status:
            query = query.filter_by(status=status)
        
        reservations = query.order_by(Reservation.created_at.desc()).all()
        
        result = []
        for res in reservations:
            user = User.query.get(res.user_id)
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            
            if lot_id and lot.id != lot_id:
                continue
            
            result.append({
                'id': res.id,
                'user_id': res.user_id,
                'user_name': user.full_name or user.username if user else 'Deleted User',
                'lot_name': lot.prime_location_name,
                'spot_number': spot.spot_number,
                'vehicle_number': res.vehicle_number,
                'parking_timestamp': format_ist_iso(res.parking_timestamp) if res.parking_timestamp else None,
                'leaving_timestamp': format_ist_iso(res.leaving_timestamp) if res.leaving_timestamp else None,
                'status': res.status,
                'payment_status': res.payment_status,
                'parking_cost': res.parking_cost or 0
            })
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/spots/<int:spot_id>', methods=['GET'])
@jwt_required()
def get_spot_details(spot_id):
    """Get detailed information about a specific parking spot"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            return jsonify({'error': 'Parking spot not found'}), 404
        
        lot = ParkingLot.query.get(spot.lot_id)
        spot_dict = spot.to_dict()
        spot_dict['lot_name'] = lot.prime_location_name
        
        # Get current reservation if occupied
        reservation_data = None
        if spot.status == 'O':
            reservation = Reservation.query.filter_by(spot_id=spot_id, status='active').first()
            if reservation:
                user = User.query.get(reservation.user_id)
                # Calculate current duration and cost
                reservation.calculate_cost(lot.price_per_hour)
                
                reservation_data = {
                    'id': reservation.id,
                    'user_id': reservation.user_id,
                    'user_name': user.full_name or user.username,
                    'vehicle_number': reservation.vehicle_number,
                    'vehicle_type': reservation.vehicle_type,
                    'parking_timestamp': format_ist_iso(reservation.parking_timestamp) if reservation.parking_timestamp else None,
                    'duration_hours': reservation.get_duration_hours(),
                    'parking_cost': reservation.parking_cost,
                    'payment_status': reservation.payment_status,
                    'status': reservation.status,
                    'remarks': reservation.remarks
                }
        
        result = {
            'spot': spot_dict,
            'lot_name': lot.prime_location_name,
            'lot_price_per_hour': lot.price_per_hour,
            'reservation': reservation_data
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/charts/parking-lots', methods=['GET'])
@jwt_required()
def get_parking_lot_chart_data():
    """Get chart data for parking lots"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        lots = ParkingLot.query.all()
        data = []
        
        for lot in lots:
            data.append({
                'name': lot.prime_location_name,
                'total_spots': lot.number_of_spots,
                'available': lot.get_available_spots_count(),
                'occupied': lot.get_occupied_spots_count()
            })
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/charts/revenue', methods=['GET'])
@jwt_required()
def get_revenue_chart_data():
    """Get revenue chart data"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get revenue for last 12 months
        data = []
        current_date = get_ist_now()
        
        for i in range(12):
            month_start = (current_date - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end = current_date
            else:
                month_end = month_start.replace(day=28) + timedelta(days=4)
                month_end = month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            revenue = db.session.query(func.sum(Reservation.parking_cost)).filter(
                Reservation.created_at >= month_start,
                Reservation.created_at < month_end,
                Reservation.payment_status == 'paid'
            ).scalar() or 0
            
            data.insert(0, {
                'month': month_start.strftime('%b %Y'),
                'revenue': round(revenue, 2)
            })
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/test-email', methods=['POST'], strict_slashes=False)
@jwt_required()
def test_email():
    """Test email configuration by sending a test email"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json() or {}
        test_email = data.get('email')
        
        # Use provided email or admin's email
        if not test_email:
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
            test_email = user.email
        
        msg = Message(
            subject='✅ Test Email - Parking Manager',
            recipients=[test_email],
            body=f"""Hello!

This is a test email from Parking Manager system.

If you received this email, your email configuration is working correctly! ✅

Email Settings:
- SMTP Server: Gmail (smtp.gmail.com)
- Port: 587
- TLS: Enabled
- Sender: Parking Manager <rkkavinraam@gmail.com>

Your scheduled jobs (Monthly Reports and Daily Reminders) should now work properly!

Best regards,
Parking Manager System

---
Sent at: {get_ist_now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        )
        
        mail.send(msg)
        
        return jsonify({
            'message': f'Test email sent successfully to {test_email}',
            'email': test_email
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Email sending failed: {error_details}")
        return jsonify({
            'error': 'Failed to send email',
            'details': str(e),
            'help': 'Check: 1) Gmail App Password is correct, 2) 2FA is enabled on Gmail, 3) SMTP settings are correct'
        }), 500

@admin_bp.route('/trigger-monthly-report', methods=['POST'], strict_slashes=False)
@jwt_required()
def trigger_monthly_report():
    """Manually trigger monthly report generation for testing"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        from backend.tasks.monthly_report import generate_monthly_reports_test
        result = generate_monthly_reports_test.delay()
        
        return jsonify({
            'message': 'Monthly report job triggered successfully (TEST MODE - current month)',
            'task_id': str(result.id),
            'status': 'Job queued. Check email in a few moments.'
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Failed to trigger monthly report: {error_details}")
        return jsonify({
            'error': 'Failed to trigger monthly report',
            'details': str(e),
            'help': 'Make sure Redis and Celery Worker are running'
        }), 500

@admin_bp.route('/trigger-daily-reminder', methods=['POST'], strict_slashes=False)
@jwt_required()
def trigger_daily_reminder():
    """Manually trigger daily reminder for testing"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        from backend.tasks.daily_reminder import send_daily_reminders
        result = send_daily_reminders.delay()
        
        return jsonify({
            'message': 'Daily reminder job triggered successfully',
            'task_id': str(result.id),
            'status': 'Job queued. Check email in a few moments.'
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Failed to trigger daily reminder: {error_details}")
        return jsonify({
            'error': 'Failed to trigger daily reminder',
            'details': str(e),
            'help': 'Make sure Redis and Celery Worker are running'
        }), 500

