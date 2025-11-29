from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import io
import csv
from backend.app import db, cache
from backend.models import Reservation, ParkingSpot, ParkingLot, User
from backend.utils.timezone import get_ist_now, format_ist_iso

reservation_bp = Blueprint('reservation', __name__)

@reservation_bp.route('/my', methods=['GET'])
@reservation_bp.route('/my/', methods=['GET'])
@jwt_required()
def get_my_reservations():
    """Get current user's reservations"""
    try:
        user_id = int(get_jwt_identity())
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
        
        result = []
        for res in reservations:
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            result.append({
                'id': res.id,
                'lot_name': lot.prime_location_name,
                'spot_number': spot.spot_number,
                'parking_timestamp': format_ist_iso(res.parking_timestamp) if res.parking_timestamp else None,
                'leaving_timestamp': format_ist_iso(res.leaving_timestamp) if res.leaving_timestamp else None,
                'status': res.status,
                'parking_cost': res.parking_cost or 0
            })
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservation_bp.route('', methods=['POST'])
@reservation_bp.route('/', methods=['POST'])
@jwt_required()
def create_reservation():
    """Create a new reservation (book a parking spot)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        spot_id = data.get('spot_id')
        if not spot_id:
            return jsonify({'error': 'spot_id is required'}), 400
        
        # Get the parking spot
        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            return jsonify({'error': 'Parking spot not found'}), 404
        
        if spot.status != 'A':
            return jsonify({'error': 'Parking spot is not available'}), 400
        
        lot = ParkingLot.query.get(spot.lot_id)
        
        # Create reservation
        reservation = Reservation(
            spot_id=spot.id,
            user_id=user_id,
            vehicle_number=data.get('vehicle_number', 'N/A'),
            vehicle_type=data.get('vehicle_type', '4-Wheeler'),
            parking_timestamp=get_ist_now(),
            status='active',
            remarks=data.get('remarks', '')
        )
        
        # Update spot status
        spot.status = 'O'
        
        db.session.add(reservation)
        db.session.commit()
        
        # Clear cache
        cache.clear()
        
        return jsonify({
            'message': 'Parking spot booked successfully',
            'reservation': {
                'id': reservation.id,
                'spot_number': spot.spot_number,
                'lot_name': lot.prime_location_name,
                'parking_timestamp': format_ist_iso(reservation.parking_timestamp)
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reservation_bp.route('/<int:reservation_id>/checkout', methods=['PUT'])
@reservation_bp.route('/<int:reservation_id>/release', methods=['POST'])
@jwt_required()
def release_reservation(reservation_id):
    """Release a parking spot (vacate)"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        # Check if user owns this reservation or is admin
        if reservation.user_id != user_id and user.role != 'admin':
            return jsonify({'error': 'Unauthorized access'}), 403
        
        if reservation.status != 'active':
            return jsonify({'error': 'Reservation is not active'}), 400
        
        # Get spot and lot information
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        
        # Update reservation
        reservation.leaving_timestamp = get_ist_now()
        reservation.status = 'completed'
        reservation.calculate_cost(lot.price_per_hour)
        
        # Update spot status
        spot.status = 'A'
        
        db.session.commit()
        
        # Clear cache
        cache.clear()
        
        return jsonify({
            'message': 'Parking spot released successfully',
            'parking_cost': reservation.parking_cost,
            'duration': reservation.get_duration_hours()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@reservation_bp.route('/user/active', methods=['GET'])
@jwt_required()
def get_user_active_reservations():
    """Get active reservations for current user"""
    try:
        user_id = int(get_jwt_identity())
        reservations = Reservation.query.filter_by(user_id=user_id, status='active').all()
        
        result = []
        for reservation in reservations:
            res_dict = reservation.to_dict()
            spot = ParkingSpot.query.get(reservation.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            res_dict['spot'] = spot.to_dict()
            res_dict['lot'] = lot.to_dict()
            result.append(res_dict)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservation_bp.route('/export', methods=['GET'])
@jwt_required()
def export_reservations():
    """Export reservations as CSV"""
    try:
        user_id = int(get_jwt_identity())
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Parking Lot', 'Spot', 'Vehicle Number', 'Check In', 'Check Out', 'Duration (hours)', 'Cost (₹)', 'Payment Status', 'Status'])
        
        for res in reservations:
            spot = ParkingSpot.query.get(res.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            writer.writerow([
                res.id,
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
        
        output.seek(0)
        
        # Create proper file response
        from io import BytesIO
        from flask import send_file
        from datetime import datetime
        
        # Convert string to bytes
        csv_bytes = BytesIO(output.getvalue().encode('utf-8'))
        csv_bytes.seek(0)
        
        filename = f'parking_history_{get_ist_now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return send_file(
            csv_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservation_bp.route('/user/history', methods=['GET'])
@jwt_required()
def get_user_reservation_history():
    """Get all reservations for current user"""
    try:
        user_id = int(get_jwt_identity())
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
        
        result = []
        for reservation in reservations:
            res_dict = reservation.to_dict()
            spot = ParkingSpot.query.get(reservation.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            res_dict['spot'] = spot.to_dict()
            res_dict['lot'] = lot.to_dict()
            result.append(res_dict)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservation_bp.route('/<int:reservation_id>', methods=['GET'])
@jwt_required()
def get_reservation(reservation_id):
    """Get specific reservation details"""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        # Check if user owns this reservation or is admin
        if reservation.user_id != user_id and user.role != 'admin':
            return jsonify({'error': 'Unauthorized access'}), 403
        
        res_dict = reservation.to_dict()
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        res_dict['spot'] = spot.to_dict()
        res_dict['lot'] = lot.to_dict()
        
        return jsonify(res_dict), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reservation_bp.route('/<int:reservation_id>/pay', methods=['POST'])
@jwt_required()
def pay_reservation(reservation_id):
    """Mark reservation as paid (dummy payment)"""
    try:
        user_id = int(get_jwt_identity())
        
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({'error': 'Reservation not found'}), 404
        
        if reservation.user_id != user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        data = request.get_json()
        payment_method = data.get('payment_method', 'card')
        
        reservation.payment_status = 'paid'
        reservation.remarks = f"Paid via {payment_method}"
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment successful',
            'reservation': reservation.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

