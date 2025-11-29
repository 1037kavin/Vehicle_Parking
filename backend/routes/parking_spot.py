from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db, cache
from backend.models import ParkingSpot, User

parking_spot_bp = Blueprint('parking_spot', __name__)

def is_admin():
    """Check if current user is admin"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return user and user.role == 'admin'

@parking_spot_bp.route('/<int:spot_id>', methods=['GET'])
def get_parking_spot(spot_id):
    """Get specific parking spot"""
    try:
        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            return jsonify({'error': 'Parking spot not found'}), 404
        return jsonify(spot.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_spot_bp.route('/available', methods=['GET'])
@cache.cached(timeout=5, query_string=True)  # Reduced from 30 to 5 seconds for development
def get_available_spots():
    """Get all available parking spots"""
    try:
        lot_id = request.args.get('lot_id', type=int)
        
        query = ParkingSpot.query.filter_by(status='A')
        if lot_id:
            query = query.filter_by(lot_id=lot_id)
        
        spots = query.all()
        return jsonify([spot.to_dict() for spot in spots]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_spot_bp.route('/occupied', methods=['GET'])
@jwt_required()
def get_occupied_spots():
    """Get all occupied parking spots (admin only)"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        spots = ParkingSpot.query.filter_by(status='O').all()
        return jsonify([spot.to_dict() for spot in spots]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_spot_bp.route('/<int:spot_id>/status', methods=['PUT'])
@jwt_required()
def update_spot_status(spot_id):
    """Update parking spot status (admin only - for blocking/unblocking)"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        spot = ParkingSpot.query.get(spot_id)
        if not spot:
            return jsonify({'error': 'Parking spot not found'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['A', 'B', 'O']:
            return jsonify({'error': 'Invalid status. Must be A (Available), B (Blocked), or O (Occupied)'}), 400
        
        # Don't allow changing occupied spots via this endpoint
        if spot.status == 'O' and new_status != 'O':
            return jsonify({'error': 'Cannot change status of occupied spot. Release reservation first.'}), 400
        
        spot.status = new_status
        db.session.commit()
        
        # Clear cache
        cache.clear()
        
        return jsonify({
            'message': f'Spot status updated to {new_status}',
            'spot': spot.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

