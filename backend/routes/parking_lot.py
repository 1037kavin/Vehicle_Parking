from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app import db, cache
from backend.models import ParkingLot, ParkingSpot, User

parking_lot_bp = Blueprint('parking_lot', __name__)

@parking_lot_bp.route('/test', methods=['POST'])
@jwt_required()
def test_jwt_post():
    """Test endpoint to verify JWT works on POST"""
    try:
        user_id = get_jwt_identity()
        return jsonify({'message': 'JWT POST works!', 'user_id': user_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def is_admin():
    """Check if current user is admin"""
    try:
        user_id = int(get_jwt_identity())
        print(f"DEBUG: User ID from token: {user_id}")
        user = User.query.get(user_id)
        print(f"DEBUG: User found: {user}, Role: {user.role if user else 'None'}")
        return user and user.role == 'admin'
    except Exception as e:
        print(f"DEBUG: Error in is_admin: {str(e)}")
        return False

@parking_lot_bp.route('', methods=['GET'])
@parking_lot_bp.route('/', methods=['GET'])
@cache.cached(timeout=5, query_string=True)  # Reduced from 60 to 5 seconds for development
def get_all_parking_lots():
    """Get all parking lots (public access)"""
    try:
        parking_lots = ParkingLot.query.filter_by(is_active=True).all()
        return jsonify([lot.to_dict() for lot in parking_lots]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_lot_bp.route('/<int:lot_id>', methods=['GET'])
@cache.cached(timeout=5)  # Reduced from 60 to 5 seconds for development
def get_parking_lot(lot_id):
    """Get specific parking lot"""
    try:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        return jsonify(lot.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@parking_lot_bp.route('', methods=['POST'])
@parking_lot_bp.route('/', methods=['POST'])
@jwt_required()
def create_parking_lot():
    """Create a new parking lot (admin only)"""
    print("DEBUG: create_parking_lot called")
    try:
        print("DEBUG: Checking admin status")
        if not is_admin():
            print("DEBUG: Not admin - returning 403")
            return jsonify({'error': 'Admin access required'}), 403
        
        print("DEBUG: Getting JSON data")
        data = request.get_json()
        print(f"DEBUG: Received data: {data}")
        
        if not data:
            print("DEBUG: No data provided")
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['prime_location_name', 'address', 'pin_code', 'price_per_hour', 'number_of_spots']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate data types
        try:
            price = float(data['price_per_hour'])
            spots = int(data['number_of_spots'])
            
            if price <= 0:
                return jsonify({'error': 'Price per hour must be greater than 0'}), 400
            if spots <= 0:
                return jsonify({'error': 'Number of spots must be greater than 0'}), 400
                
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
        
        # Create parking lot
        lot = ParkingLot(
            prime_location_name=data['prime_location_name'],
            address=data['address'],
            pin_code=data['pin_code'],
            price_per_hour=price,
            number_of_spots=spots,
            description=data.get('description', '')
        )
        
        db.session.add(lot)
        db.session.flush()  # Get the lot.id
        
        # Create parking spots automatically
        for i in range(1, lot.number_of_spots + 1):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=f"S{i:03d}",
                status='A',
                floor_number=((i - 1) // 20) + 1  # 20 spots per floor
            )
            db.session.add(spot)
        
        db.session.commit()
        
        # Clear all cache to ensure fresh data
        cache.clear()
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'parking_lot': lot.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error creating parking lot: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to create parking lot: {str(e)}'}), 500

@parking_lot_bp.route('/<int:lot_id>', methods=['PUT'])
@jwt_required()
def update_parking_lot(lot_id):
    """Update parking lot (admin only)"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        data = request.get_json()
        
        # Update basic fields
        if 'prime_location_name' in data:
            lot.prime_location_name = data['prime_location_name']
        if 'address' in data:
            lot.address = data['address']
        if 'pin_code' in data:
            lot.pin_code = data['pin_code']
        if 'price_per_hour' in data:
            lot.price_per_hour = float(data['price_per_hour'])
        if 'description' in data:
            lot.description = data['description']
        
        # Handle number_of_spots change
        if 'number_of_spots' in data:
            new_count = int(data['number_of_spots'])
            current_count = lot.number_of_spots
            
            if new_count > current_count:
                # Add new spots
                for i in range(current_count + 1, new_count + 1):
                    spot = ParkingSpot(
                        lot_id=lot.id,
                        spot_number=f"S{i:03d}",
                        status='A',
                        floor_number=((i - 1) // 20) + 1
                    )
                    db.session.add(spot)
            elif new_count < current_count:
                # Remove extra spots (only if they are available)
                spots_to_remove = ParkingSpot.query.filter_by(
                    lot_id=lot.id, status='A'
                ).order_by(ParkingSpot.id.desc()).limit(current_count - new_count).all()
                
                if len(spots_to_remove) < (current_count - new_count):
                    return jsonify({'error': 'Cannot reduce spots, some are occupied'}), 400
                
                for spot in spots_to_remove:
                    db.session.delete(spot)
            
            lot.number_of_spots = new_count
        
        db.session.commit()
        
        # Clear all cache to ensure fresh data
        cache.clear()
        
        return jsonify({
            'message': 'Parking lot updated successfully',
            'parking_lot': lot.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parking_lot_bp.route('/<int:lot_id>', methods=['DELETE'])
@jwt_required()
def delete_parking_lot(lot_id):
    """Delete parking lot (admin only, only if all spots are empty)"""
    try:
        if not is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        # Check if all spots are available
        occupied_count = lot.get_occupied_spots_count()
        if occupied_count > 0:
            return jsonify({'error': f'Cannot delete. {occupied_count} spots are occupied'}), 400
        
        db.session.delete(lot)
        db.session.commit()
        
        # Clear all cache to ensure fresh data
        cache.clear()
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@parking_lot_bp.route('/<int:lot_id>/spots', methods=['GET'])
@cache.cached(timeout=5)  # Reduced from 30 to 5 seconds for development
def get_lot_spots(lot_id):
    """Get all spots for a parking lot"""
    try:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return jsonify({'error': 'Parking lot not found'}), 404
        
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return jsonify([spot.to_dict() for spot in spots]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

