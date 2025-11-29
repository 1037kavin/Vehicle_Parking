from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
import io
from backend.app import db
from backend.models import User, Reservation, ParkingSpot, ParkingLot

user_bp = Blueprint('user', __name__)

@user_bp.route('/stats', methods=['GET'])
@user_bp.route('/stats/', methods=['GET'])
@user_bp.route('/dashboard', methods=['GET'])
@user_bp.route('/dashboard/', methods=['GET'])
@jwt_required()
def get_user_dashboard():
    """Get user dashboard statistics"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get statistics
        total_reservations = Reservation.query.filter_by(user_id=user_id).count()
        active_reservations = Reservation.query.filter_by(user_id=user_id, status='active').count()
        completed_reservations = Reservation.query.filter_by(user_id=user_id, status='completed').count()
        
        # Total spent
        total_spent = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.user_id == user_id,
            Reservation.status == 'completed'
        ).scalar() or 0
        
        # Most used parking lot
        most_used_lot_query = db.session.query(
            ParkingLot.prime_location_name,
            func.count(Reservation.id).label('count')
        ).join(
            ParkingSpot, ParkingSpot.lot_id == ParkingLot.id
        ).join(
            Reservation, Reservation.spot_id == ParkingSpot.id
        ).filter(
            Reservation.user_id == user_id
        ).group_by(
            ParkingLot.id
        ).order_by(
            func.count(Reservation.id).desc()
        ).first()
        
        most_used_lot = most_used_lot_query[0] if most_used_lot_query else 'N/A'
        
        # Monthly spending for chart
        monthly_spending = []
        current_date = datetime.utcnow()
        for i in range(6):  # Last 6 months
            month_start = (current_date - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_end = month_start.replace(day=28) + timedelta(days=4) if i > 0 else current_date
            if i > 0:
                month_end = month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            spent = db.session.query(func.sum(Reservation.parking_cost)).filter(
                Reservation.user_id == user_id,
                Reservation.created_at >= month_start,
                Reservation.created_at < month_end,
                Reservation.status == 'completed'
            ).scalar() or 0
            
            monthly_spending.insert(0, {
                'month': month_start.strftime('%b'),
                'amount': round(spent, 2)
            })
        
        # Most used parking lots
        most_used_lots = db.session.query(
            ParkingLot.prime_location_name,
            func.count(Reservation.id).label('count')
        ).join(
            ParkingSpot, ParkingSpot.lot_id == ParkingLot.id
        ).join(
            Reservation, Reservation.spot_id == ParkingSpot.id
        ).filter(
            Reservation.user_id == user_id
        ).group_by(
            ParkingLot.id
        ).order_by(
            func.count(Reservation.id).desc()
        ).limit(5).all()
        
        most_used_lots_data = [{'name': name, 'count': count} for name, count in most_used_lots]
        
        # This month spending
        month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_spent = db.session.query(func.sum(Reservation.parking_cost)).filter(
            Reservation.user_id == user_id,
            Reservation.created_at >= month_start,
            Reservation.status == 'completed'
        ).scalar() or 0
        
        return jsonify({
            'total_bookings': total_reservations,
            'active_reservations': active_reservations,
            'total_spent': round(total_spent, 2),
            'monthly_spent': round(monthly_spent, 2),
            'most_used_lots': most_used_lots_data,
            'monthly_spending': monthly_spending
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/charts/monthly-usage', methods=['GET'])
@jwt_required()
def get_monthly_usage_chart():
    """Get monthly usage chart data"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get data for last 12 months
        data = []
        current_date = datetime.utcnow()
        
        for i in range(12):
            month_start = (current_date - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if i == 0:
                month_end = current_date
            else:
                month_end = month_start.replace(day=28) + timedelta(days=4)
                month_end = month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            count = Reservation.query.filter(
                Reservation.user_id == user_id,
                Reservation.created_at >= month_start,
                Reservation.created_at < month_end
            ).count()
            
            spent = db.session.query(func.sum(Reservation.parking_cost)).filter(
                Reservation.user_id == user_id,
                Reservation.created_at >= month_start,
                Reservation.created_at < month_end,
                Reservation.status == 'completed'
            ).scalar() or 0
            
            data.insert(0, {
                'month': month_start.strftime('%b %Y'),
                'bookings': count,
                'spent': round(spent, 2)
            })
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@user_bp.route('/profile/', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@user_bp.route('/profile/', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            user.email = data['email']
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not user.check_password(data.get('current_password', '')):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        user.set_password(data['new_password'])
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/export-csv/download', methods=['GET'])
@jwt_required()
def download_csv_export():
    """Direct download CSV export (synchronous)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get all reservations
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
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
        
        # Prepare file for download
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'parking_history_{user_id}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/parking-lot-preferences', methods=['GET'])
@jwt_required()
def get_parking_lot_preferences():
    """Get user's parking lot usage statistics"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get parking lot usage
        lot_usage = db.session.query(
            ParkingLot.id,
            ParkingLot.prime_location_name,
            func.count(Reservation.id).label('usage_count'),
            func.sum(Reservation.parking_cost).label('total_spent')
        ).join(
            ParkingSpot, ParkingSpot.lot_id == ParkingLot.id
        ).join(
            Reservation, Reservation.spot_id == ParkingSpot.id
        ).filter(
            Reservation.user_id == user_id
        ).group_by(
            ParkingLot.id
        ).order_by(
            func.count(Reservation.id).desc()
        ).all()
        
        data = []
        for lot_id, lot_name, usage_count, total_spent in lot_usage:
            data.append({
                'lot_id': lot_id,
                'lot_name': lot_name,
                'usage_count': usage_count,
                'total_spent': round(total_spent or 0, 2)
            })
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

